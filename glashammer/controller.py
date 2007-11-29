
from glashammer.service import Service
from glashammer.utils import TemplateResponse


class ControllerService(Service):

    def lifecycle(self):
        self.controllers = {}

    def register(self, name, controller):
        self.controllers[name] = controller

    def get(self, name):
        return self.controllers.get(name)


class Controller(object):

    def __init__(self, site,):
        self.site = site
        self.jinja = self.site.jinja_service.env

    def __before__(self, req, *args):
        pass

    def __after__(self, req, *args):
        pass

    def create_template_response(self, req, name, **kw):
        return TemplateResponse(self.site, name, kw, req=req, controller=self)

    def list_feature_providers(self, feature):
        return self.site.feature_service.list(feature)


