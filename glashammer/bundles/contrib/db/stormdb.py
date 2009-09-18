"""
glashammer.bundles.stormdb
~~~~~~~~~~~~~~~~~~~~~~~~~~

Storm integration for Glashammer. (inspired by storm.zope.zstorm)

Most of this module is concerned with issues relating to thread-locality of
store instances. It is important that each thread, and thus each request has
it's own store, and then subsequently closes that store to clean up at the end
of the request.

During the two phases of the Glashammer application, a store manager will be
created thread locally for:

1. During application setup the store(s) are available for use in the
`data` initialization functions, so any required data can be added.

2. During the request phase the store(s) are available for general database
activities required by the application.

During each of these phases we must create and bind an instance of the
:class:`StoreManager` to the thread local instance, at the start of the phase,
and clean it up at the end. This is achieved using the Glashammer system
events:

`app-start`
    After the application setup functions have been called, but no data has been
    initialised. Thus the store manager is available during data initialization.
`app-setup`
    At the end of the application setup phase, the store manager is cleaned up.
`wsgi-call`
    This is emitted at the very start of the request as the WSGI application is
    called. We use it here to initialize the store manager.
`response-end`
    This is emitted at the end of the request, and is used to clean up the store
    manager.
"""

from os.path import join

from storm.locals import *

from glashammer.utils import local, get_app

class StoreManager(object):
    """
    Thread local instance holding database and stores.

    `dburi`
        The database URI used to open stores.
    """

    def __init__(self, dburi):
        self._dburi = dburi
        self._stores = {}
        self._db = None

    def get(self, name):
        """
        Retrieve or create the named store.
        """
        if name in self._stores:
            return self._stores.get(name)
        else:
            return self.create(name)

    def create(self, name):
        """
        Create a named store for the database.
        """
        if not self._db:
            self._db = create_database(self._dburi)
        store = Store(self._db)
        self._stores[name] = store
        return store

    def close_all(self):
        """
        Close all stores, and remove them from the manager. For cleanup.
        """
        for store in self._stores.values():
            store.close()
        self._stores = {}


def close_all(arg):
    """
    Close all stores for the thread local instance of the store manager.
    """
    local.storm_stores_manager.close_all()


def initialize_manager(*args):
    """
    Ensure there is a thread local isntance of the stores manager.
    """
    if not hasattr(local, 'storm_stores_manager'):
        local.storm_stores_manager = StoreManager(get_app().conf['stormdb/dburi'])


def get_store(name='default'):
    """
    Get the thread local store.

    `name`
        Optional argument to retrieve a named store.
    """
    return local.storm_stores_manager.get(name)


def setup_stormdb(app, default_uri=None):
    """
    Setup the Storm integration.

    `default_uri`
        The default URI to set for the database. This value can be overriden in
        any configuration file. If no default URI is provided, an in-memory
        SQLite database is used where no instance directory is provided to the
        application, or a file-based database `gh.sqlite` is created in the
        instance directory.
    """
    if not default_uri:
        if app.instance_dir:
            default_uri = 'sqlite:%s' % join(app.instance_dir, 'gh.sqlite')
        else:
            default_uri = 'sqlite:'

    app.add_config_var('stormdb/dburi', str, default_uri)

    app.connect_event('app-start', initialize_manager)
    app.connect_event('app-setup', close_all)
    app.connect_event('wsgi-call', initialize_manager)
    app.connect_event('response-end', close_all)

setup_app = setup_stormdb
