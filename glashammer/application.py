

import os
from time import time

from werkzeug import ClosingIterator, SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from glashammer.simpleconfig import SimpleConfig
from glashammer.config import Configuration

from glashammer.templating import create_template_environment

from glashammer.utils import local, local_manager, EventManager, emit_event, \
    url_for, sibpath, Request, Response, _, format_datetime

from glashammer.database import db

from glashammer import htmlhelpers


DEFAULT_CONFIG = [
    ('db_uri', '', str),
    ('session_cookie_name', 'glashammer_session', str),
    ('secret_key', 'my secret', str),
    ('base_url', u'', str),
]


def default_setup_func(app):
    from glashammer.bundles.auth import setup as auth_setup
    # XXX shouldn't really need this
    app.add_setup(auth_setup)
    app.add_template_searchpath(sibpath(__file__, 'templates'))


class GlashammerApplication(object):
    """WSGI Application"""

    default_setup = default_setup_func

    def __init__(self, setup_func, instance_dir):
        # just for playing in the shell
        local.application = self

        self.finalized = False

        # Start the setup
        self.instance_dir = os.path.abspath(instance_dir)
        self.config_file = os.path.join(self.instance_dir, 'config.ini')

        if not os.path.exists(self.instance_dir):
            raise RunTimeError('Application instance directory missing')

        #self.conf = SimpleConfig(DEFAULT_CONFIG)
        self.conf = self.cfg = Configuration(self.config_file)

        for name, default, type in DEFAULT_CONFIG:
            self.add_config_var(name, type, default)

        # Create a config file if one doesn't exist
        # Otherwise, merge the current file
        if not os.path.exists(self.config_file):
            db_file = os.path.join(self.instance_dir, 'gh.sqlite')
            self.cfg['db_uri'] = 'sqlite:///' + db_file
            self.cfg.save()

        self.map = Map()
        self.views = {}
        self.controllers = {}
        self.events = EventManager(self)

        # Temporary variables for collecting setup information

        # Template stuff
        self._template_searchpaths = []
        self._template_globals = {}
        self._template_filters = {}
        self._layout_template = None

        # shared
        self._shared_exports = {}

        # Setup functions (basically plugins)
        self._setup_funcs = set()
        self._osetup_funcs = []

        # Data initialization functions
        self._data_funcs = set()
        self._odata_funcs = []

        # setup the default stuff
        self.default_setup()

        # setup the application
        setup_func(self)

        # run the additional setup funcions
        for setup_func in self._osetup_funcs:
            setup_func(self)

        del self._setup_funcs

        # Now the database

        self.db_engine = db.create_engine(self.cfg['db_uri'],
                                          convert_unicode=True)

        for data_func in self._odata_funcs:
            data_func(self.db_engine)

        del self._data_funcs



        self._template_globals.update({
            'url_for': url_for,
            'layout_template': self._layout_template,
            '_': _,
            'cfg': self.cfg,
            'request':local('request'),
            'h': htmlhelpers,
        })

        self._template_filters.update({
            'datetimeformat': format_datetime
        })

        # create the template environment
        self.template_env = create_template_environment(
            searchpaths=self._template_searchpaths,
            globals=self._template_globals,
            filters=self._template_filters,
        )

        del self._template_searchpaths
        del self._layout_template


        # now add the middleware for static file serving
        #self.add_shared_exports('core', SHARED_DATA)
        self.add_middleware(SharedDataMiddleware, self._shared_exports)

        del self._shared_exports

        # finalize the setup
        self.finalized = True
        # create the template environment
        emit_event('app-setup')

    def __call__(self, environ, start_response):
        return ClosingIterator(self.dispatch_request(environ, start_response),
                               [local_manager.cleanup])

    def dispatch_request(self, environ, start_response):
        local.application = self
        local.url_adapter = adapter = self.map.bind_to_environ(environ)
        local.request = request = Request(self, environ)
        emit_event('app-request', request)
        try:
            endpoint, values = adapter.match()
            response = self.get_view(request, endpoint, values)
        except HTTPException, e:
            response = e
        # cleanup
        emit_event('app-response', response)

        # save the session
        if request.session.should_save:
            cookie_name = self.conf['session_cookie_name']
            if request.session.get('pmt'):
                max_age = 60 * 60 * 24 * 31
                expires = time() + max_age
            else:
                max_age = expires = None
            request.session.save_cookie(response, cookie_name, max_age=max_age,
                                        expires=expires, session_expires=expires)
        return response(environ, start_response)


    def get_view(self, request, endpoint, values):
        # try looking up by view first
        view = self.views.get(endpoint)
        if view is None:
            # fallback to controller->view
            controller = self.controllers.get(endpoint.split('/', 1)[0])
            if controller is not None and hasattr(controller, endpoint.split('/', 1)[1]):
                return getattr(controller, endpoint.split('/', 1)[0])(request, **values)
            else:
                # fallback to notfound
                return NotFound()
        return view(request, **values)

    def _prefinalize_only(f):
        def _decorated(self, *args, **kw):
            if self.finalized:
                raise RuntimeError('Already Finalized')
            return f(self, *args, **kw)
        return _decorated


    @_prefinalize_only
    def add_setup(self, setup_func):
        """Add a setup callable to be called on startup by the application.

        This method is used to add pluggable capability to the application.
        For example, plugin A can load plugin B by importing and adding it's
        setup func.

        ::
            >>> from glashammer.bundles.admin import setup
            >>> app.add_setup(setup)

        Will initialize the admin interface for the application.
        """
        if setup_func not in self._setup_funcs:
            self._setup_funcs.add(setup_func)
            self._osetup_funcs.append(setup_func)

    @_prefinalize_only
    def add_data_func(self, data_func):
        if data_func not in self._data_funcs:
            self._data_funcs.add(data_func)
            self._odata_funcs.append(data_func)

    @_prefinalize_only
    def add_bundle(self, bundle):
        self.add_setup(bundle.setup)

    @_prefinalize_only
    def add_url(self, url, endpoint, view=None, **kw):
        rule = Rule(url, endpoint=endpoint, **kw)
        if view is not None:
            self.views[endpoint] = view
        self.map.add(rule)

    @_prefinalize_only
    def add_view(self, endpoint, view):
        self.views[endpoint] = view
    
    @_prefinalize_only
    def add_controller(self, endpoint, controller):
        self.controllers[endpoint] = controller

    @_prefinalize_only
    def add_template_searchpath(self, path):
        path = os.path.abspath(path)
        self._template_searchpaths.append(path)

    @_prefinalize_only
    def add_template_global(self, key, value):
        self._template_globals[key] = value

    @_prefinalize_only
    def connect_event(self, event, callback, position='after'):
        """Connect an event to the current application."""
        return self.events.connect(event, callback, position)

    @_prefinalize_only
    def set_layout_template(self, template_name):
        self._layout_template = template_name

    @_prefinalize_only
    def add_shared(self, name, path):
        """Add a shared export for name that points to a given path and
        creates an url rule for <name>/shared that takes a filename
        parameter.
        """
        self._shared_exports['/_shared/' + name] = path
        self.add_url('/_shared/%s/<string:filename>' % name,
                     endpoint=name + '/shared', build_only=True)

    @_prefinalize_only
    def add_middleware(self, middleware_factory, *args, **kwargs):
        """Add a middleware to the application."""
        self.dispatch_request = middleware_factory(self.dispatch_request,
                                                   *args, **kwargs)

    @_prefinalize_only
    def add_config_var(self, key, type, default):
        """Add a configuration variable to the application."""
        if key.count('/') > 1:
            raise ValueError('key might not have more than one slash')
        self.cfg.config_vars[key] = (type, default)


def make_app(setup_func, instance_dir):
    """Create an application instance.

    `setup_func`   The callable used by the application to set itself up. This
                   is the main entry point into the application.

    `instance_dir` The directory where instance-related files will be stored.
    """
    application = local('application')
    application = GlashammerApplication(setup_func, instance_dir)
    application = local_manager.make_middleware(application)
    return application


