# -*- coding: utf-8 -*-
"""
    glashammer.bundles.sqlalchdb
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2008-2010 by Ali Afshar
                2010 by Pascal Hartig
    :license: MIT
"""


import os

from sqlalchemy import create_engine, orm, MetaData
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.exc import InvalidRequestError

from werkzeug.exceptions import NotFound

from glashammer.utils import get_app
from glashammer.utils.local import local, local_manager
from glashammer.utils.config import config_overriding_val


# a new scoped session
session = orm.scoped_session(lambda: orm.create_session(
                             local.application.sqla_db_engine,
                             autoflush=True, autocommit=False),
                             local_manager.get_ident)

#XXX: add a way to get metadata by name

metadata = MetaData()
mapper = orm.mapper
models = set()


class Query(orm.Query):
    """Default query class."""

    def first(self, raise_if_missing=False):
        """Return the first result of this `Query` or None if the result
        doesn't contain any row.  If `raise_if_missing` is set to `True`
        a `NotFound` exception is raised if no row is found.
        """
        rv = orm.Query.first(self)
        if rv is None and raise_if_missing:
            raise NotFound()
        return rv


class ModelBaseMeta(DeclarativeMeta):
    """Model Metadata to store a copy of all models."""

    def __init__(cls, name, bases, dct):
        if '__tablename__' in dct:
            models.add(cls)

        super(ModelBaseMeta, cls).__init__(name, bases, dct)


class MetaModel(object):
    """Give models the ability to perform simple operations on themselves.
    """

    query = session.query_property(Query)

    def __init__(self, *args, **kwargs):
        super(object, self).__init__(*args, **kwargs)

        session.expunge(self)

    def pre_save(self, **kwargs):
        pass

    def post_save(self, is_new, **kwargs):
        pass

    def save(self, **kwargs):
        self.pre_save(**kwargs)

        is_new = getattr(self, list(self.__class__.__table__.primary_key)[0].key) is None
        try:
            session.flush([self])
        except InvalidRequestError:
            session.rollback()

            session.flush([self])

        assert getattr(self, list(self.__class__.__table__.primary_key)[0].key) is not None
        self.post_save(is_new=is_new, **kwargs)

    def delete(self):
        is_new = getattr(self, list(self.__class__.__table__.primary_key)[0].key) is None

        if not is_new:
            session.delete(self)
            session.flush([self])
        else:
            session.expunge(self)


ModelBase = declarative_base(metadata=metadata, name="ModelBase", cls=MetaModel, metaclass=ModelBaseMeta)


def get_engine():
    """Get the SQLA DB Engine"""
    return get_app().sqla_db_engine


def data_init(app):
    app.sqla_db_meta.create_all(bind=app.sqla_db_engine)


def cleanup_sqla_session(arg):
    session.remove()

# XXX Replace this with real config options using YAML

def _parse_opts(opts):
    """
        >>> _parse_opts('hello=world,foo=bar')
        {'hello': 'world', 'foo': 'bar'}
    """

    ret = dict()
    for entry in opts.strip().split(','):
        key, value = entry.split('=')
        if value in ('True', 'true'):
            value = True
        elif value in ('False', 'false'):
            value = False

        ret[key] = value

    return ret


def setup_sqlalchdb(app, default_uri=None, metadata=metadata):
    default = 'sqlite:///%s' % os.path.join(app.instance_dir, 'gh.sqlite')
    db_uri = config_overriding_val(app, default, default_uri, 'db/uri', str)
    app.add_config_var('database/opts', str, '')
    app.connect_event('response-end', cleanup_sqla_session)
    app.connect_event('app-setup', cleanup_sqla_session)

    db_opts = app.cfg['database/opts']
    option_kwargs = len(db_opts) > 0 and _parse_opts(db_opts) or dict()
    app.sqla_db_engine = create_engine(db_uri, **option_kwargs)
    app.sqla_db_meta = metadata
    app.add_data_func(data_init)


setup_app = setup_sqlalchdb



