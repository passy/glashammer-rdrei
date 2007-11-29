
from glashammer.service import Service

class ControllerService(Service):

    def lifecycle(self):
        self.controllers = {}

    def register(self, name, controller):
        self.controllers[name] = controller

    def get(self, name):
        return self.controllers.get(name)


class Controller(object):

    def __init__(self, site, req, environ):
        self.site = site
        self.req = req
        self.environ = environ
        self.jinja = self.site.jinja_service.env
        self.session = self.environ['werkzeug.session']
        self.user_id = self.environ.get('glashammer.user_id')
        self.map_adapter = self.site.routing_service.bind_to_environ(environ)

    def __before__(self, req, *args):
        pass

    def __after__(self, req, *args):
        pass

    def create_template_response(self, name, **kw):
        return TemplateResponse(self.site, name, kw, req=self.req, controller=self)

    def list_feature_providers(self, feature):
        return self.site.feature_service.list(feature)


