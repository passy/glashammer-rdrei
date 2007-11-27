

from werkzeug.serving import run_simple
from werkzeug.routing import NotFound, RequestRedirect, Map
from werkzeug.utils import SharedDataMiddleware
from werkzeug.contrib.sessions import SessionMiddleware, FilesystemSessionStore
from werkzeug.local import Local, LocalManager

from glashammer.utils import Request, NotFoundResponse, RedirectResponse
from glashammer.config import SiteConfig
from glashammer.auth import AuthService
from glashammer.stormintegration import ThreadSafeStorePool
from glashammer.layout import LayoutService
from glashammer.jinjaintegration import create_jinja_environment


class GlashammerApplication(object):
    """WSGI Application"""

    def __init__(self, site):
        self.site = site
        self.config = site.config

    def __call__(self, environ, start_response):
        url_adapter = self.site.url_map.bind_to_environ(environ)
        req = Request(environ, url_adapter)
        try:
            endpoint, args = url_adapter.match(req.path)
            resp = self._get_response(environ, endpoint, args, req)
        except NotFound:
            resp = NotFoundResponse()
        except RequestRedirect, e:
            resp = RedirectResponse(e.new_url)
        return resp(environ, start_response)

    def _get_controller(self, endpoint_name):
        return self.site.controllers.get(endpoint_name, None)

    def _get_response(self, environ, endpoint, args, req):
        endpoint_name, endpoint_method = endpoint.split('/', 1)
        controller_type = self._get_controller(endpoint_name)
        if controller_type is None:
            resp = NotFoundResponse()
        else:
            controller = controller_type(self.site, req, environ)
            method = getattr(controller, endpoint_method, None)
            if method is None:
                resp = NotFoundResponse()
            else:
                controller.__before__(req, *args)
                resp = method(req, *args)
                controller.__after__(req, *args)
        return resp



class GlashammerSite(object):
    """
    Site. This is the boss that controls everything else, including the
    WSGI application
    """

    def __init__(self):
        self.config = SiteConfig()
        self.controllers = {}
        self.url_map = Map()
        self.services = []
        self.static_directories = {}
        self.template_directories = []
        self.storm_uri = 'sqlite:test.sqlite'
        self.tables = []
        # Thread local stuff
        self._local = Local()
        self._localmanager = LocalManager([self._local])

        # services
        self.layout_service = self.register_service(LayoutService)
        self.auth_service = self.register_service(AuthService)

    def finalise_config(self):
        # Last thing before app is created
        self.jinja_environment = create_jinja_environment(
            self.template_directories)
        self.store_pool = ThreadSafeStorePool(self._local, self.storm_uri)
        for svc in self.services:
            svc.finalise()

    def get_store(self):
        return self.store_pool.get()

    store = property(get_store)

    def make_app(self):
        self.finalise_config()
        app = GlashammerApplication(self)
        app = self._make_static_app(app)
        app = self._make_authed_app(app)
        app = self._make_sessioned_app(app)
        app = self._make_localed_app(app)
        return app

    def _make_static_app(self, app):
        static_map = dict(self.static_directories)
        app = SharedDataMiddleware(app, static_map)
        app.site = self
        return app

    def _make_sessioned_app(self, app):
        app = SessionMiddleware(app, FilesystemSessionStore('.'))
        app.site = self
        return app

    def _make_authed_app(self, app):
        return self.auth_service.create_middleware(app)

    def _make_localed_app(self, app):
        return self._localmanager.make_middleware(app)

    def register_controller(self, name, controller):
        self.controllers[name] = controller
    
    def register_static_directory(self, name, path):
        self.static_directories[name] = path

    def register_template_directory(self, path):
        self.template_directories.insert(0, path)

    def register_url_rules(self, *rules):
        for rule in rules:
            self.url_map.add(rule)

    def register_database_table(self, table):
        self.tables.append(table)
        table.create_table(self.store)

    def register_service(self, service_class):
        svc = service_class(self)
        self.services.append(svc)
        return svc

    def run_debug_server(self, host='localhost', port=8080, autoreload=True):
        run_simple(host, port, self.make_app(), autoreload)

