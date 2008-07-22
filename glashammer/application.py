
"""
The Glashammer Application.
"""

import os

from werkzeug import ClosingIterator, SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from glashammer.config import Configuration

from glashammer.templating import create_template_environment

from glashammer.utils import local, local_manager, EventManager, emit_event, \
    url_for, sibpath, Request



def default_setup_func(app):
    app.add_template_searchpath(sibpath(__file__, 'templates'))


class GlashammerApplication(object):
    """WSGI Application"""

    default_setup = default_setup_func

    def __init__(self, setup_func, instance_dir=None, config_factory=None):
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

        #for name, default, type in DEFAULT_CONFIG:
        #    self.add_config_var(name, type, default)

        # Create a config file if one doesn't exist
        # Otherwise, merge the current file
        #if not os.path.exists(self.config_file):
        #    self.cfg.save()

        self.map = Map()
        self.views = {}
        self.controllers = {}
        self.events = EventManager(self)

        # permanent things you can use during setup
        self.request_processors = []
        self.response_processors = []
        self.local_processors = []

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


        for data_func in self._odata_funcs:
            data_func(self)

        del self._data_funcs



        self._template_globals.update({
            'url_for': url_for,
            'layout_template': local('layout_template'),
            'cfg': self.cfg,
            'request':local('request'),
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
        for proc in self.local_processors:
            proc(local)
        emit_event('app-request', request)
        for proc in self.request_processors:
            proc(request)
        try:
            endpoint, values = adapter.match()
            request.endpoint = endpoint
            request.values = values
            response = self.get_view(request, endpoint, values)
        except HTTPException, e:
            response = e
        # cleanup
        emit_event('app-response', response)


        for proc in self.response_processors:
            proc(response)
        return response(environ, start_response)

    def get_view(self, request, endpoint, values):
        # try looking up by view first
        view = self.views.get(endpoint)
        if view is None:
            # fallback to controller->view
            base, target = endpoint.split('/', 1)
            controller = self.controllers.get(base)
            if controller is not None and hasattr(controller, target):
                return getattr(controller, target)(request, **values)
            else:
                # fallback to notfound
                return NotFound()
        return view(request, **values)

    def _prefinalize_only(f):
        def _decorated(self, *args, **kw):
            if self.finalized:
                raise RuntimeError('Already Finalized')
            return f(self, *args, **kw)
        _decorated.__doc__ = f.__doc__
        _decorated.__name__ = f.__name__
        _decorated.__module__ = f.__module__
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
        """Add a template global"""
        self._template_globals[key] = value

    def add_template_filter(self, name, f):
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

    @_prefinalize_only
    def add_request_processor(self, processor):
        self.request_processors.append(processor)

    @_prefinalize_only
    def add_response_processor(self, processor):
        self.response_processors.append(processor)

    @_prefinalize_only
    def add_local_processor(self, processor):
        self.local_processors.append(processor)


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


