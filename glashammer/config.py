

from plugins import Registry


# some tokens
URL_MAP_TOKEN = 'url-map'
ENDPOINT_TOKEN = 'endpoint'
SHARED_TOKEN = 'shared'


class SiteConfig(object):

    def __init__(self):
         self._registry = Registry()

    def set_url_map(self, url_map):
        self._registry.register_singleton(URL_MAP_TOKEN, url_map)

    def get_url_map(self):
        return self._registry.get_singleton(URL_MAP_TOKEN)

    def register_controller(self, endpoint_name, controller):
        self._registry.register_singleton(
            (ENDPOINT_TOKEN, endpoint_name), controller)

    def get_controller(self, endpoint_name):
        return self._registry.get_singleton((ENDPOINT_TOKEN, endpoint_name))

    def set_templates_dir(self):
        pass

    def register_static_dir(self, name, directory):
        self._registry.register_feature(SHARED_TOKEN, (name, directory))

    def get_static_dirs(self):
        return self._registry.get_feature_providers(SHARED_TOKEN)

    
