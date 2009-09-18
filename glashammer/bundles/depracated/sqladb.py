# -*- coding: utf-8 -*-
"""
    glashammer.bundles.sqladb
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2007 by Armin Ronacher, Ali Afshar, Christopher Grebs, Pedro
                Algarvio
    :license: MIT
"""

import os

import warnings

from datetime import datetime, timedelta

from types import ModuleType

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.util import to_list

from glashammer.utils import local, local_manager, get_app


def mapper(*args, **kwargs):
    """
    Add our own database mapper, not the new sqlalchemy 0.4
    session aware mapper.
    """
    kwargs['extension'] = extensions = to_list(kwargs.get('extension', []))
    extensions.append(ManagerExtension())
    return orm.mapper(*args, **kwargs)


class ManagerExtension(orm.MapperExtension):
    """
    Use django like database managers.
    """

    def get_session(self):
        return session.registry()

    def instrument_class(self, mapper, class_):
        managers = []
        for key, value in class_.__dict__.iteritems():
            if isinstance(value, DatabaseManager):
                managers.append(value)
        if not managers:
            if hasattr(class_, 'objects'):
                raise RuntimeError('The model %r already has an attribute '
                                   'called "objects".  You have to either '
                                   'rename this attribute or defined a '
                                   'mapper yourself with a different name')
            class_.objects = mgr = DatabaseManager()
            managers.append(mgr)
        class_._tp_managers = managers
        for manager in managers:
            manager.bind(class_)

    def init_instance(self, mapper, class_, oldinit, instance, args, kwargs):
        session = kwargs.pop('_sa_session', self.get_session())
        if not kwargs.pop('_tp_no_save', False):
            entity = kwargs.pop('_sa_entity_name', None)
            session._save_impl(instance, entity_name=entity)
        return orm.EXT_CONTINUE

    def init_failed(self, mapper, class_, oldinit, instance, args, kwargs):
        orm.object_session(instance).expunge(instance)
        return orm.EXT_CONTINUE


class DatabaseManager(object):
    """
    Baseclass for the database manager which you can also subclass to add
    more methods to it and attach to models by hand.  An instance of this
    manager is added to model classes automatically as `objects` unless there
    is at least one model manager specified on the class.

    Example for custom managers::

        class UserManager(DatabaseManager):

            def authors(self):
                return self.filter(User.role >= ROLE_AUTHOR)


        class User(object):
            objects = UserManager()

    :meth:`bind` is called with the reference to the model automatically by
    the mapper extension to bind the manager to the model.
    """

    def __init__(self):
        self.model = None

    def bind(self, model):
        """Called automatically by the `ManagerExtension`."""
        if self.model is not None:
            raise RuntimeError('manager already bound to model')
        self.model = model

    def __getitem__(self, arg):
        return self.query[arg]

    @property
    def query(self):
        """Return a new queryset."""
        return session.registry().query(self.model)

    def all(self):
        """Return all objects."""
        return self.query.all()

    def first(self):
        """Return the first object."""
        return self.query.first()

    def one(self):
        """
        Return the first result of all objects, raising an exception if
        more than one row exists.
        """
        return self.query.one()

    def get(self, *args, **kwargs):
        """Look up an object by primary key."""
        return self.query.get(*args, **kwargs)

    def filter(self, arg):
        """Filter all objects by the criteron provided and return a query."""
        return self.query.filter(arg)

    def filter_by(self, **kwargs):
        """Filter by keyword arguments."""
        return self.query.filter_by(**kwargs)

    def order_by(self, arg):
        """Order by something."""
        return self.query.order_by(arg)

    def limit(self, limit):
        """Limit all objects."""
        return self.query.limit(limit)

    def offset(self, offset):
        """Return a query with an offset."""
        return self.query.offset(offset)

    def count(self):
        """Count all posts."""
        return self.query.count()



#: a new scoped session
session = orm.scoped_session(lambda: orm.create_session(
                             local.application.sqla_db_engine,
                             autoflush=True, transactional=True),
                             local_manager.get_ident)

#: create a new module for all the database related functions and objects
db = ModuleType('db')
key = value = mod = None
for mod in sqlalchemy, orm:
    for key, value in mod.__dict__.iteritems():
        if key in mod.__all__:
            setattr(db, key, value)
del key, mod, value

db.__doc__ = __doc__
db.mapper = mapper
db.get_engine = lambda: local.application.database_engine
for name in 'delete', 'save', 'flush', 'execute', 'begin', \
            'commit', 'rollback', 'clear', 'refresh', 'expire':
    setattr(db, name, getattr(session, name))
db.session = session
db.DatabaseManager = DatabaseManager

#: support for SQLAlchemy's 0.4.2 Text type, in older versions it's
#: just Text.  This patch will go away once SQLAlchemy 0.5 is out
#: or something like that.
if not hasattr(db, 'Text'):
    db.Text = db.String

#: called at the end of a request
cleanup_session = session.remove

#: metadata for the core tables and the core table definitions
metadata = db.MetaData()


from glashammer.utils.json import JsonRestService

class JsonSqlaRestService(JsonRestService):

    def modify(self, response):
        return response

    def get_table(self):
        return NotImplementedError

    def create_results_set(self, q):
        """Reference implementation.

        Override for specific behaviour
        """
        objs = [self._serialize(o) for o in q]
        return objs

    def query(self, **kw):
        return self.create_results_set(self.get_table().objects.filter_by(**kw))

    def get(self, req, **kw):
        return self.query(**kw)

    def post(self, req, **kw):
        o = self.get_table()()
        for k in req.form:
            setattr(o, k, req.form.get(k))
        db.commit()
        return self.create_results_set([o])

    def _serialize(self, obj):
        if hasattr(obj, 'json_serializer'):
            pass
        else:
            # naive
            d = {}
            for a in dir(obj):
                attr = getattr(obj, a)
                if (isinstance(attr, (basestring, int, float)) and
                    not a.startswith('_')):
                    d[a] = attr
            return d


class JsonSqlaSerializer(object):
    pass


def init_database(engine):
    """
    This is also called form the upgrade database function but especially from
    the websetup. That's also why it takes an engine and not a textpress
    application.
    """
    metadata.create_all(engine)


def upgrade_database(app):
    """
    Check if the tables are up to date and perform an upgrade.
    Currently creating is enough. Once there are release verisons
    this function will upgrade the database structure too.
    """
    init_database(app.database_engine)


def _get_default_db_uri(app):
    db_file = os.path.join(app.instance_dir, 'gh.sqlite')
    return 'sqlite:///' + db_file

def get_engine():
    """Get the SQLA DB Engine"""
    return get_app().sqla_db_engine

def data_init(app):
    metadata.create_all()

def cleanup_sqla_session(arg):
    session.remove()

def setup_sqladb(app, default_db_uri=None):
    warnings.warn("The sqladb bundle is depracated. Use sqlalchdb", DeprecationWarning)
    if default_db_uri is None:
        default_db_uri = _get_default_db_uri(app)
    app.add_config_var('sqla_db_uri', str, default_db_uri)
    app.connect_event('response-end', cleanup_sqla_session)
    app.connect_event('app-setup', cleanup_sqla_session)
    app.sqla_db_engine = db.create_engine(app.cfg['sqla_db_uri'],
                                          convert_unicode=True)
    print app.sqla_db_engine
    metadata.bind = app.sqla_db_engine
    app.add_data_func(data_init)

setup_app = setup_sqladb
