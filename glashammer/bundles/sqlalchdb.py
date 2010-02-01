# -*- coding: utf-8 -*-
"""
    glashammer.bundles.sqlalchdb
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2008-2010 by Ali Afshar, Pascal Hartig, Plurk Inc
    :license: MIT
"""

from __future__ import with_statement
import sys
import time
import os
from threading import Lock
from datetime import datetime
from babel import Locale
from sqlalchemy.types import TypeDecorator
from sqlalchemy.engine.url import make_url
from sqlalchemy.interfaces import ConnectionProxy
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.interfaces import SessionExtension, MapperExtension, \
     EXT_CONTINUE
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.util import to_list
from sqlalchemy import String, orm, sql, create_engine, MetaData

from glashammer.utils.config import config_overriding_val
from glashammer.utils.lazysettings import LazySettings
from glashammer.utils.local import local_manager, get_request
from glashammer.utils import emit_event
from werkzeug.exceptions import NotFound


_engine = None
_engine_lock = Lock()

#XXX: add a way to get metadata by name

metadata = MetaData()
settings = LazySettings()
models = set()

# the best timer for the platform. on windows systems we're using clock
# for timing which has a higher resolution.
if sys.platform == 'win32':
    _timer = time.clock
else:
    _timer = time.time


def get_engine():
    """Get the SQLAlchemy DB Engine

    This returns the global SQLALchemy engine, which is *usually* shared amongst all
    threads. If there has no engine been initialized yet, one is created.
    """
    global _engine
    with _engine_lock:
        if _engine is None:
            options = {'echo': settings['database/echo'],
                       'convert_unicode': True}
            if settings['database/track_queries']:
                options['proxy'] = ConnectionQueryTrackingProxy()
            uri = make_url(settings['database/uri'])

            # if mysql is the database engine and no connection encoding is
            # provided we set it to the mysql charset (defaults to utf8)
            # and set up a mysql friendly pool
            if uri.drivername == 'mysql':
                uri.query.setdefault('charset', 'utf8')
                options['pool_recycle'] = \
                        settings['database/mysql_pool_recycle']
            _engine = create_engine(uri, **options)
        return _engine


def refresh_engine():
    """Gets rid of the existing engine.  Useful for unittesting, use with care.
    Do not call this function if there are multiple threads accessing the
    engine.  Only do that in single-threaded test environments or console
    sessions.
    """
    global _engine
    with _engine_lock:
        session.remove()
        if _engine is not None:
            _engine.dispose()
        _engine = None


def atomic_add(obj, column, delta, expire=False):
    """Performs an atomic add (or subtract) of the given column on the
    object.  This updates the object in place for reflection but does
    the real add on the server to avoid race conditions.  This assumes
    that the database's '+' operation is atomic.

    If `expire` is set to `True`, the value is expired and reloaded instead
    of added of the local value.  This is a good idea if the value should
    be used for reflection.
    """
    sess = orm.object_session(obj) or session
    mapper = orm.object_mapper(obj)
    pk = mapper.primary_key_from_instance(obj)
    assert len(pk) == 1, 'atomic_add not supported for classes with ' \
                         'more than one primary key'

    val = orm.attributes.get_attribute(obj, column)
    if expire:
        orm.attributes.instance_state(obj).expire_attributes([column])
    else:
        orm.attributes.set_committed_value(obj, column, val + delta)

    table = mapper.tables[0]
    stmt = sql.update(table, mapper.primary_key[0] == pk[0], {
        column:     table.c[column] + delta
    })
    sess.execute(stmt)


def mapper(model, table, **options):
    """A mapper that hooks in standard extensions."""
    extensions = to_list(options.pop('extension', None), [])
    extensions.append(SignalTrackingMapperExtension())
    options['extension'] = extensions
    return orm.mapper(model, table, **options)


class ConnectionQueryTrackingProxy(ConnectionProxy):
    """A proxy that if enabled counts the queries."""

    def cursor_execute(self, execute, cursor, statement, parameters,
                       context, executemany):
        emit_event('before-cursor-executed', cursor=self, statement=statement,
                                    parameters=parameters)
        start = _timer()
        try:
            return execute(cursor, statement, parameters, context)
        finally:
            emit_event('after-cursor-executed',
                       cursor=self,
                       statement=statement,
                       parameters=parameters,
                       time=_timer() - start)


class SignalTrackingMapperExtension(MapperExtension):
    """Remembers model changes for the session commit code."""

    def after_delete(self, mapper, connection, instance):
        return self._record(instance, 'delete')

    def after_insert(self, mapper, connection, instance):
        return self._record(instance, 'insert')

    def after_update(self, mapper, connection, instance):
        return self._record(instance, 'update')

    def _record(self, model, operation):
        pk = tuple(orm.object_mapper(model).primary_key_from_instance(model))
        orm.object_session(model)._model_changes[pk] = (model, operation)
        return EXT_CONTINUE


class SignalEmittingSessionExtension(SessionExtension):
    """Emits signals the mapper extension accumulated."""

    def before_commit(self, session):
        d = session._model_changes
        if d:
            emit_event('before_models_committed', changes=d.values())
        return EXT_CONTINUE

    def after_commit(self, session):
        d = session._model_changes
        if d:
            emit_event('after_models_committed', changes=d.values())
            d.clear()
        return EXT_CONTINUE

    def after_rollback(self, session):
        session._model_changes.clear()
        return EXT_CONTINUE


class SignalTrackingSession(Session):
    """A session that tracks signals for later"""

    def __init__(self):
        extension = [SignalEmittingSessionExtension()]
        Session.__init__(self, get_engine(), autoflush=True,
                         autocommit=False, extension=extension)
        self._model_changes = {}


session = orm.scoped_session(SignalTrackingSession, local_manager.get_ident)


class LocaleType(TypeDecorator):
    """A locale in the database."""

    impl = String

    def __init__(self):
        TypeDecorator.__init__(self, 10)

    def process_bind_param(self, value, dialect):
        if value is None:
            return
        return unicode(str(value))

    def process_result_value(self, value, dialect):
        if value is not None:
            return Locale.parse(value)

    def is_mutable(self):
        return False


class ModelBaseMeta(DeclarativeMeta):
    """Model Metadata to store a reference to all model types."""

    def __init__(cls, name, bases, dct):
        if '__tablename__' in dct:
            models.add(cls)

        super(ModelBaseMeta, cls).__init__(name, bases, dct)


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
        """Save this object in the database.
        """
        self.pre_save(**kwargs)
        session.add(self)
        is_new = self in session.new
        try:
            session.flush()
        except InvalidRequestError:
            session.rollback()
            session.flush()

        self.post_save(is_new=is_new, **kwargs)

    def delete(self):
        """Remove this object from the database.
        """

        is_new = getattr(self, list(self.__class__.__table__.primary_key)[0].key) is None

        if not is_new:
            session.delete(self)
            session.flush([self])
        else:
            session.expunge(self)


ModelBase = declarative_base(metadata=metadata, name="ModelBase", cls=MetaModel, metaclass=ModelBaseMeta)


def data_init(app):
    """The default data init function.

    The Sqlalch bundle automatically calls this data init function after the
    application is first created. This ensures that all tables are created for
    the metadata, so Metdata.create_all does not need to be called again.
    """
    engine = get_engine()
    if engine.name == 'mysql':
        for table in metadata.tables.itervalues():
            table.kwargs.update(mysql_engine=settings['database/mysql_engine'],
                                mysql_charset=settings['database/mysql_table_charset'])
    metadata.create_all(bind=engine)


def cleanup_sqla_session(app):
    """Clean the current session. Session is a thread-local scoped session, so
    this can safely be used from within a request, knowing that it will not
    affect sessions within other threads.

    It is unlikely that this function will be called manually, the sqlalch
    bundle connects the event `response-end` to call this function, which
    takes care of cleaning up sessions after each request/response.
    """
    session.remove()


def drop_tables():
    """Drops all tables again."""
    metadata.drop_all(bind=get_engine())


def add_query_debug_headers(request, response):
    """Add headers with the SQL info."""
    if settings['database/track_queries']:
        count = len(request.sql_queries)
        sql_time = 0.0
        for stmt, param, time in request.sql_queries:
            sql_time += time
        response.headers['X-SQL-Query-Count'] = str(count)
        response.headers['X-SQL-Query-Time'] = str(sql_time)


def request_track_query(cursor, statement, parameters, time):
    """If there is an active request, it logs the query on it."""
    if settings['database/track_queries']:
        # It's possible we're not in a request. This happens e. g. in test
        # cases.
        try:
            request = get_request()
        except AttributeError:
            pass
        else:
            # Users can use their own wrappers that does not necessarilly have
            # an sql_queries attribute. We create our own here, if this happens.
            if not hasattr(request, 'sql_queries'):
                request.sql_queries = list()

            request.sql_queries.append((statement, parameters, time))


def setup_sqlalchdb(app, default_uri=None, metadata=metadata, initdb=True):
    """Database setup function. Use ``application.add_setup(setup_database)``
    to initialize database use.

    :param app: The Glashammer application object.
    :param default_uri: Override the uri settings from the config.
    :param initdb: Set False to not automatically run create_all
    on metadata on application setup. Use :func:``data_init`` to manually
    initialize the database.
    """

    default = 'sqlite:///%s' % os.path.join(app.instance_dir, 'gh.sqlite')
    app.add_config_var('database/echo', bool, False)
    app.add_config_var('database/uri', str, '')
    app.add_config_var('database/track_queries', bool, False)
    app.add_config_var('database/mysql_pool_recycle', int, 300)
    app.add_config_var('database/mysql_engine', str, 'InnoDB')
    app.add_config_var('database/mysql_table_charset', str, 'utf8')

    app.connect_event('response-end', lambda response:
                      add_query_debug_headers(None, response))
    app.connect_event('response-end', cleanup_sqla_session)
    app.connect_event('app-setup', cleanup_sqla_session)
    app.connect_event('after-cursor-executed', request_track_query)

    if initdb:
        app.add_data_func(data_init)

    db_uri = config_overriding_val(app, default, default_uri, 'database/uri', str)

    global settings
    settings.bind(app)

    app.sqla_db_engine = get_engine()
    app.sqla_db_meta = metadata
