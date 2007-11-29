

class Service(object):

    def __init__(self, site):
        self.site = site
        self.lifecycle()

    def lifecycle(self):
        pass

    def finalise(self):
        pass

    def setup(self):
        """
        This is called when you first want to set up your application.

        Use it to create database tables and initial data.
        """
        pass

    def create_middleware(self, app):
        raise NotImplementedError

    def get_store(self):
        return self.site.storm_service.store

    store = property(get_store)

    def register_static_directory(self, name, path):
        self.site.static_service.register(name, path)

    def register_url_rules(self, *rules):
        self.site.routing_service.register(*rules)

    def register_controller(self, name, controller):
        self.site.controller_service.register(name, controller)

    def register_template_directory(self, path):
        self.site.jinja_service.register(path)

    def register_config(self, name, default=None):
        self.site.config_service.register(name, default)

    def register_feature_provider(self, feature, provider):
        self.site.feature_service.register(feature, provider)

    def list_feature_providers(self, feature):
        return self.site.feature_service.list(feature)




