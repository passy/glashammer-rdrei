

from werkzeug.serving import run_simple
from werkzeug.routing import NotFound, RequestRedirect, Map
from werkzeug.utils import SharedDataMiddleware

from glashammer.utils import Request, NotFoundResponse, RedirectResponse
from glashammer.config import ConfigService
from glashammer.auth import AuthService
from glashammer.stormintegration import StormService
from glashammer.layout import LayoutService
from glashammer.jinjaintegration import create_jinja_environment
from glashammer.plugins import Registry
from glashammer.statics import StaticService
from glashammer.jinjaintegration import JinjaService
from glashammer.controller import ControllerService
from glashammer.routing import RoutingService
from glashammer.sessions import SessionService
from glashammer.features import FeatureService

import warnings


class GlashammerApplication(object):
    """WSGI Application"""

    def __init__(self, site):
        self.site = site
        self.controller_cache = {}

    def __call__(self, environ, start_response):
        url_adapter = self.site.routing_service.bind_to_environ(environ)
        req = Request(environ, url_adapter)
        try:
            endpoint, args = url_adapter.match(req.path)
            resp = self._get_response(environ, endpoint, args, req)
        except NotFound:
            resp = NotFoundResponse()
        except RequestRedirect, e:
            resp = RedirectResponse(e.new_url)
        return resp(environ, start_response)

    def _get_response(self, environ, endpoint, args, req):
        endpoint_name, endpoint_method = endpoint.split('/', 1)
        try:
            controller = self.controller_cache[endpoint_name]
        except KeyError:
            controller = self._create_controller(endpoint)
        if controller is None:
            resp = NotFoundResponse()
        else:
            method = getattr(controller, endpoint_method, None)
            if method is None:
                resp = NotFoundResponse()
            else:
                controller.__before__(req, *args)
                resp = method(req, *args)
                controller.__after__(req, *args)
        return resp
            
    def _create_controller(self, endpoint):
        controller_type = self._get_controller(endpoint_name)
        if controller_type is not None:
            controller = controller_type(self.site)
            return controller

    def _get_controller(self, endpoint_name):
        return self.site.controller_service.get(endpoint_name)



class GlashammerSite(object):
    """
    Site. This is the boss that controls everything else, including the
    WSGI application
    """

    def __init__(self, site_config):
        self.services = []
        self.site_config = site_config
        # core services
        self.config_service = self.register_service(ConfigService)
        self.storm_service = self.register_service(StormService)
        self.controller_service = self.register_service(ControllerService)
        self.static_service = self.register_service(StaticService)
        self.jinja_service = self.register_service(JinjaService)
        self.routing_service = self.register_service(RoutingService)
        self.auth_service = self.register_service(AuthService)
        self.layout_service = self.register_service(LayoutService)
        self.session_service = self.register_service(SessionService)
        self.feature_service = self.register_service(FeatureService)

    def finalise(self):
        for svc in self.services:
            svc.finalise()

    def setup_site(self):
        self.finalise()
        for svc in self.services:
            svc.setup()

    def make_app(self):
        self.finalise()
        app = GlashammerApplication(self)
        return self.make_service_app(app)

    def make_service_app(self, app):
        for svc in self.services:
            try:
                app = svc.create_middleware(app)
            except NotImplementedError:
                pass
        return app

    def register_service(self, service_class):
        svc = service_class(self)
        self.services.append(svc)
        return svc
        
    def run_debug_server(self, host='localhost', port=8080, autoreload=True):
        run_simple(host, port, self.make_app(), autoreload)


