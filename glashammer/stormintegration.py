

from cgi import escape

from storm.locals import Storm, Store, Int, Unicode, create_database

from werkzeug.local import Local, LocalManager

from glashammer.service import Service


class StormCreator(Storm):

    @classmethod
    def _get_type_for_var(cls, col):
        name = col._name
        vtype = col._variable_class.__name__
        if vtype == 'IntVariable':
            if col._primary:
                vname = 'INTEGER PRIMARY KEY'
            else:
                vname = 'INTEGER'
        elif vtype == 'DateVariable':
            vname = 'DATE'
        elif vtype == 'UnicodeVariable':
            vname = 'VARCHAR'
        elif vtype == 'BoolVariable':
            vname = 'BOOL'
        elif vtype == 'FloatVariable':
            vname = 'FLOAT'
        elif vtype == 'TimeVariable':
            vname = 'TIME'
        else:
            raise TypeError('Unknown Type: %s (%s)' %
                (col._name, vtype))
        return '%s %s' % (name, vname)

    @classmethod
    def create_table(cls, store):
        cols = []
        for col, prop in cls._storm_columns.items():
            cols.append(cls._get_type_for_var(col))
        q = 'CREATE TABLE %s (%s)' % (cls.__storm_table__, ', '.join(cols))
        store.execute(q)
        print 'create', cls


class StormBase(StormCreator):

    id = Int(primary=True)


def create_store(uri):
    return Store(create_database(uri))


class ThreadSafeStorePool(object):

    def __init__(self, local, uri):
        self._db = create_database(uri)
        self._local = local

    def get(self):
        try:
            return self._local.store
        except AttributeError:
            self._local.store = Store(self._db)
            return self._local.store


class StormService(Service):

    def lifecycle(self):
        self.local = Local()
        self.local_manager = LocalManager([self.local])

    def finalise(self):
        self.store_pool = ThreadSafeStorePool(self.local, self.site.storm_uri)

    def get_store(self):
        return self.store_pool.get()

    def create_middleware(self, app):
        return self.local_manager.make_middleware(app)

    store = property(get_store)
