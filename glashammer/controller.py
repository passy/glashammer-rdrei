
from glashammer.bundle import Bundle
from glashammer.utils import TemplateResponse


class ControllerBundle(Bundle):

    def lifecycle(self):
        self.controllers = {}

    def register(self, name, controller):
        self.controllers[name] = controller

    def get(self, name):
        return self.controllers.get(name)


class Controller(object):

    def __init__(self, site,):
        self.site = site

    def __before__(self, req, *args):
        pass

    def __after__(self, req, *args):
        pass

    def create_template_response(self, req, name, **kw):
        return TemplateResponse(self.site, name, kw, req=req, controller=self)

    # XXX May not be the right place for this
    def list_feature_providers(self, feature):
        return self.site.feature.list(feature)


