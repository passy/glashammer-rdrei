"""
glashammer.bundles.stormdb
~~~~~~~~~~~~~~~~~~~~~~~~~~

Storm integration for Glashammer
"""

from os.path import join

from storm.locals import *

from glashammer.utils import local, get_app

class StoreManager(object):
    """
    Thread local instance holding database and stores.
    """

    def __init__(self, dburi):
        self._dburi = dburi
        self._stores = {}
        self._db = None

    def get(self, name):
        if name in self._stores:
            return self._stores.get(name)
        else:
            return self.create(name)

    def create(self, name):
        if not self._db:
            self._db = create_database(self._dburi)
        store = Store(self._db)
        self._stores[name] = store
        return store

    def close_all(self):
        for store in self._stores.values():
            store.close()
        self._stores = {}

def close_all(arg):
    local.storm_stores_manager.close_all()

def setup_manager(*args):
    if not hasattr(local, 'storm_stores_manager'):
        local.storm_stores_manager = StoreManager(get_app().conf['stormdb/dburi'])

def get_store(name='default'):
    return local.storm_stores_manager.get(name)


def setup_stormdb(app, default_uri=None):
    if not default_uri:
        if app.instance_dir:
            default_uri = 'sqlite:%s' % join(app.instance_dir, 'gh.sqlite')
        else:
            default_uri = 'sqlite:'

    app.add_config_var('stormdb/dburi', str, default_uri)

    app.connect_event('app-start', setup_manager)
    app.connect_event('app-setup', close_all)
    app.connect_event('wsgi-call', setup_manager)
    app.connect_event('response-end', close_all)

setup_app = setup_stormdb
