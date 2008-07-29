
"""
The Glashammer Application.
"""

import os

from werkzeug import ClosingIterator, SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from glashammer.utils.config import Configuration

from glashammer.utils.templating import create_template_environment

from glashammer.utils import local, local_manager, EventManager, emit_event, \
    url_for, sibpath, Request



def default_setup_func(app):
    app.add_template_searchpath(sibpath(__file__, 'templates'))


class GlashammerApplication(object):
    """WSGI Application"""

    default_setup = default_setup_func

    def __init__(self, setup_func, instance_dir=None):
        # just for playing in the shell
        local.application = self

        self.finalized = False

        # Start the setup
        if instance_dir is None:
            instance_dir = os.path.dirname(__file__)

        self.instance_dir = os.path.abspath(instance_dir)

        self.config_file = os.path.join(self.instance_dir, 'config.ini')

        if not os.path.exists(self.instance_dir):
            raise RuntimeError('Application instance directory missing')

        self.conf = self.cfg = Configuration(self.config_file)

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
        for setup_func, args in self._osetup_funcs:
            setup_func(self, *args)

        del self._setup_funcs

        # Now the database


        for data_func in self._odata_funcs:
            data_func(self)

        del self._data_funcs



        self._template_globals.update({
            'url_for': url_for,
            'layout_template': local('layout_template'),
            'cfg': self.cfg,
            'request':local('request'),
            'emit_event':self.events.template_emit
        })

        self._template_filters.update({
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
        self.add_shared('glashammer', sibpath(__file__, 'shared'))
        self.add_middleware(SharedDataMiddleware, self._shared_exports)

        del self._shared_exports

        # finalize the setup
        self.finalized = True
        # create the template environment
        emit_event('app-setup', self)

    def __call__(self, environ, start_response):
        return ClosingIterator(self.dispatch_request(environ, start_response),
                               [local_manager.cleanup])

    def dispatch_request(self, environ, start_response):
        local.application = self
        local.url_adapter = adapter = self.map.bind_to_environ(environ)
        local.request = request = Request(self, environ)
        emit_event('request-start', request)
        try:
            endpoint, values = adapter.match()
            request.endpoint = endpoint
            request.values = values
            emit_event('request-end', request)
            response = self.get_view(request, endpoint, values)
        except HTTPException, e:
            response = e
        emit_event('response-start', response)
        resp = response(environ, start_response)
        emit_event('response-end', response)
        return resp

    def get_view(self, request, endpoint, values):
        # try looking up by view first
        view = self.views.get(endpoint)
        if view:
            return view(request, **values)
        elif '/' in endpoint:
            # fallback to controller->view
            base, target = endpoint.split('/', 1)
            controller = self.controllers.get(base)
            if controller is not None and hasattr(controller, target):
                return getattr(controller, target)(request, **values)
        return NotFound()


    def _prefinalize_only(f):
        def _decorated(self, *args, **kw):
            if self.finalized:
                raise RuntimeError('Already Finalized')
            return f(self, *args, **kw)
        _decorated.__doc__ = f.__doc__
        _decorated.__name__ = f.__name__
        _decorated.__module__ = f.__module__
        return _decorated

    def add_setup(self, setup_func, *args):
        """Add a setup callable to be called on startup by the application.

        `setup_func`
            The callable to be called during application setup.

        `*args`
            Arguments that will be passed to the setup function

        This method is used to add pluggable capability to the application.
        For example, plugin A can load plugin B by importing and adding it's
        setup func like so::

            >>> from a import setup
            >>> app.add_setup(setup)

        Or in a real example::

            >>> from glashammer.bundles.auth import setup_app
            >>> app.add_setup(setup_app)

        Will initialize the auth bundle for the application.
        """
        vals = (setup_func, args)
        if vals not in self._setup_funcs:
            self._setup_funcs.add(vals)
            self._osetup_funcs.append(vals)

    @_prefinalize_only
    def add_data_func(self, data_func):
        """
        Add a data callable to be called after the setup callables
        """
        if data_func not in self._data_funcs:
            self._data_funcs.add(data_func)
            self._odata_funcs.append(data_func)

    @_prefinalize_only
    def add_bundle(self, bundle):
        """
        Add a bundle (a module or other thing with a setup_app callable
        """
        self.add_setup(bundle.setup_app)

    @_prefinalize_only
    def add_url(self, url, endpoint, view=None, **kw):
        """
        Register a url for an endpoint, optionally register a view with it.
        """
        rule = Rule(url, endpoint=endpoint, **kw)
        self.add_url_rule(rule, view)

    def add_url_rule(self, rule, view=None):
        """
        Add a url rule with optional view
        """
        self.map.add(rule)
        if view is not None:
            self.views[rule.endpoint] = view

    def add_url_rules(self, rules):
        """
        Add a list of rules to the map
        """
        for rule in rules:
            self.map.add(rule)

    @_prefinalize_only
    def add_view(self, endpoint, view):
        """
        Register a view for an endpoint
        """
        self.views[endpoint] = view

    @_prefinalize_only
    def add_views_controller(self, endpoint_base, controller):
        """
        Add a an instance or module which contains functions for a number of
           views.

        'endpoint_base` The base end point
        'controller` A module or instance to search for views in.

        This method allows you to add multiple views from a source. It is useful
        in situations where it is desirable to add many views at once for a certain
        endpoint's base.

        For example::

            app.add_url('/foo', 'foo/index')
            app.add_url('/foo/add', 'foo/add')

            class Controller(object):

                def index(self):
                    ...

                def add(self):
                    ...

            app.add_views_controller('foo', Controller())

        Here, the endpoint's base is 'foo'. And the actual endpoints will be the
        attribute names concatenated with the endpoint_base.

        """

        self.controllers[endpoint_base] = controller

    @_prefinalize_only
    def add_template_searchpath(self, path):
        """Add a directory to the template search path"""
        path = os.path.abspath(path)
        self._template_searchpaths.append(path)

    @_prefinalize_only
    def add_template_global(self, key, value):
        """
        Add a template global variable.

        `key`
            The variable name
        `value`
            The variable value. Note that you can use a proxy to a local
            variable by using glashammer.utils.local('<variable name>').
        """
        self._template_globals[key] = value

    def add_template_filter(self, name, f):
        """
        Add a template filter.
        """
        self._template_filters[name] = f

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


