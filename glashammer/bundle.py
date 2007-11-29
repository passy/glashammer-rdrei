

class Bundle(object):

    def __init__(self, site):
        self.site = site
        self.lifecycle()

    # Overridable bundle API

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

    def process_request(self, req):
        return req

    def process_response(self, resp, req):
        return resp

    def get_priority(self):
        return 100

    def create_middleware(self, app):
        raise NotImplementedError


    # Database Access
    def get_store(self):
        return self.site.storm.store

    store = property(get_store)

    # Registering activities for the bundle
    def register_static_directory(self, name, path):
        self.site.static.register(name, path)

    def register_url_rules(self, *rules):
        self.site.routing.register(*rules)

    def register_controller(self, name, controller):
        self.site.controller.register(name, controller)

    def register_template_directory(self, path):
        self.site.jinja.register(path)

    def register_config(self, name, default=None):
        self.site.config.register(name, default)

    def register_feature_provider(self, feature, provider):
        self.site.feature.register(feature, provider)

    # Listing features provided by the bundle
    def list_feature_providers(self, feature):
        return self.site.feature.list(feature)




