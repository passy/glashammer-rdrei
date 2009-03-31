
"""
glashammer.application
~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2008 Glashammer Developers
:license: MIT

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
    """WSGI Application

    This should usually be made using the :func:`make_app` function, which
    additionally wraps the application in threadlocal session cleaning code.

    `setup_func`
        The callable to be called to initialize the application

    `instance_dir`
        The directory to use for instance-specific information

    `config_name`
        The name of the configuration file in the instance directory

    `config_factory`
        The dict-like class that will be used for configuration. This is
        provided in situations where a file-based configuration file is not
        suitable, such as AppEngine.

    `url_map`
        A werkzeug.routing.Map instance. Additional application rules will
        be added to this. If this is not provided a new Map will be created
        by default.

    `view_map`
        A map of endpoints to view callables. Views added during setup will
        be added to this map. If it is not provided, a new dict is created.

    `template_searchpaths`
        A list of paths to search for templates. Additional paths added
        during application setup will be added to this list. If none is
        provided a new list will be created (default).

    `template_filters`
        A mapping of name to callable which are template filters. Additional
        filters will be added to this map before the template environment is
        created. If none is provided a new dict is created (default).

    `template_globals`
        A mapping of name to variable which will be available in the
        template's global namespace. Additional variables added during
        application setup will be added to this map. If this is not provided
        a new dict will be created.
    """

    default_setup = default_setup_func

    def __init__(self, setup_func,
        instance_dir=None,
        config_name='config.ini', config_factory=Configuration,
        url_map=None, view_map=None,
        template_searchpaths=None, template_filters=None, template_globals=None,
        template_tests=None,
        template_env_kw=None,
        ):
        # just for playing in the shell
        local.application = self

        self.finalized = False

        # Start the setup
        if instance_dir is None:
            instance_dir = os.path.dirname(__file__)

        self.instance_dir = os.path.abspath(instance_dir)

        self.config_file = os.path.join(self.instance_dir, config_name)

        if not os.path.exists(self.instance_dir):
            raise RuntimeError('Application instance directory missing')

        self.conf = self.cfg = Configuration(self.config_file)

        if url_map:
            self.map = url_map
        else:
            self.map = Map()

        if view_map:
            self.views = view_map
        else:
            self.views = {}

        self.controllers = {}

        self.events = EventManager(self)

        # Temporary variables for collecting setup information

        # Template stuff
        if template_searchpaths:
            self._template_searchpaths = template_searchpaths
        else:
            self._template_searchpaths = []

        if template_globals:
            self._template_globals = template_globals
        else:
            self._template_globals = {}

        if template_filters:
            self._template_filters = template_filters
        else:
            self._template_filters = {}
        
        if template_tests:
            self._template_tests = template_tests
        else:
            self._template_tests = {}

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
        for setup_func, args, kw in self._osetup_funcs:
            setup_func(self, *args, **kw)

        del self._osetup_funcs

        emit_event('app-start', self)

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
            tests=self._template_tests,
            env_kw=template_env_kw,
        )

        del self._template_searchpaths
        del self._layout_template


        # now add the middleware for static file serving
        self.add_shared('glashammer', sibpath(__file__, 'shared'))
        self.add_middleware(SharedDataMiddleware, self._shared_exports)

        # now the middleware for cleaning up things
        self.add_middleware(local_manager.make_middleware)

        # Keep this hanging around for introspection
        self.shared_export_map = self._shared_exports

        del self._shared_exports

        # finalize the setup
        self.finalized = True
        # create the template environment
        emit_event('app-setup', self)

    def __call__(self, environ, start_response):
        local.application = self
        emit_event('wsgi-call')
        emit_event('wsgi-env', environ)
        return ClosingIterator(self.dispatch_request(environ, start_response),
                               [local_manager.cleanup])

    def dispatch_request(self, environ, start_response):
        local.url_adapter = adapter = self.map.bind_to_environ(environ)
        local.request = request = Request(self, environ)
        emit_event('request-start', request)
        try:
            endpoint, values = adapter.match()
            request.endpoint = endpoint
            request.endpoint_values = values
            emit_event('request-end', request)
            response = self.get_view(request, endpoint, values)
        except HTTPException, e:
            emit_event('request-error', e)
            response = e.get_response(environ)
        emit_event('response-start', response)
        resp = response(environ, start_response)
        emit_event('response-end', resp)
        return resp

    def get_view(self, request, endpoint, values):
        emit_event('view-dispatch', endpoint, values)
        # try looking up by view first
        view = self.views.get(endpoint)
        if view:
            emit_event('view-match', view)
            return view(request, **values)
        elif '/' in endpoint or '.' in endpoint:
            # fallback to controller->view
            if '/' in endpoint:
                base, target = endpoint.split('/', 1)
            else:
                base, target = endpoint.split('.', 1)
            controller = self.controllers.get(base)
            if controller is not None and hasattr(controller, target):
                emit_event('controller-match', controller, target)
                return getattr(controller, target)(request, **values)
        raise NotFound()

    def _ensure_not_finalized(self):
        if self.finalized:
            raise RuntimeError('You cannot do this. The application has been finalized.')

    def add_setup(self, setup_func, *args, **kw):
        """Add a setup callable to be called on startup by the application.

        `setup_func`
            The callable to be called during application setup.

        `*args`
            Arguments that will be passed to the setup function

        `**kw`
            Keyword arguments that will be passed to the setup function

        This method is used to add pluggable capability to the application.
        For example, plugin A can load plugin B by importing and adding it's
        setup func like so::

            >>> from a import setup_a
            >>> app.add_setup(setup_a)

        Or in a real example::

            >>> from glashammer.bundles.auth import setup_auth
            >>> app.add_setup(setup_auth)

        Will initialize the auth bundle for the application.
        """
        self._ensure_not_finalized()

        vals = (setup_func, args, kw)

        if vals not in self._osetup_funcs:
            self._osetup_funcs.append(vals)

    def add_data_func(self, data_func):
        """
        Add a data callable to be called after the setup callables
        """
        self._ensure_not_finalized()

        if data_func not in self._data_funcs:
            self._data_funcs.add(data_func)
            self._odata_funcs.append(data_func)

    def add_bundle(self, bundle, *args, **kw):
        """
        Add a bundle (a module or other thing with a setup_app callable
        """
        self._ensure_not_finalized()

        self.add_setup(bundle.setup_app, *args, **kw)

    def add_url(self, url, endpoint, view=None, **kw):
        """
        Register a url for an endpoint, optionally register a view with it.
        """
        self._ensure_not_finalized()

        rule = Rule(url, endpoint=endpoint, **kw)
        self.add_url_rule(rule, view)

    def add_url_rule(self, rule, view=None):
        """
        Add a url rule with optional view
        """
        self._ensure_not_finalized()

        self.map.add(rule)
        if view is not None:
            self.views[rule.endpoint] = view

    def add_url_rules(self, rules):
        """
        Add a list of rules to the map
        """
        self._ensure_not_finalized()

        for rule in rules:
            self.map.add(rule)

    def add_view(self, endpoint, view):
        """
        Register a view for an endpoint
        """
        self._ensure_not_finalized()

        self.views[endpoint] = view

    def add_views_controller(self, endpoint_base, controller):
        """
        Add an instance or module which contains functions for a number of
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
        self._ensure_not_finalized()

        self.controllers[endpoint_base] = controller

    def add_template_searchpath(self, path):
        """
        Add a directory to the template search path
        """
        self._ensure_not_finalized()

        path = os.path.abspath(path)
        self._template_searchpaths.append(path)

    def add_template_global(self, key, value):
        """
        Add a template global variable.

        `key`
            The variable name
        `value`
            The variable value. Note that you can use a proxy to a local
            variable by using glashammer.utils.local('<variable name>').
        """
        self._ensure_not_finalized()

        self._template_globals[key] = value

    def add_template_filter(self, name, f):
        """
        Add a template filter.
        """
        self._ensure_not_finalized()

        self._template_filters[name] = f

    def add_template_test(self, name, f):
        """
        Add a template filter.
        """
        self._ensure_not_finalized()
        
        self._template_tests[name] = f

    def connect_event(self, event, callback, position='after'):
        """
        Connect an event to the current application.
        """
        self._ensure_not_finalized()

        return self.events.connect(event, callback, position)

    def set_layout_template(self, template_name):
        self._ensure_not_finalized()

        self._layout_template = template_name

    def add_shared(self, name, path):
        """
        Add a shared export for name that points to a given path and
        creates an url rule for shared/<name> that takes a filename
        parameter.
        """
        self._ensure_not_finalized()

        #Allow empty name
        if name == '':
            sep = ''
        else:
            sep = '/'

        url = sep.join(['/_shared', name])
        ep = sep.join(['shared', name])

        self._shared_exports[url] = path
        self.add_url('%s/<string:filename>' % url,
                     endpoint=ep, build_only=True)

    def add_middleware(self, middleware_factory, *args, **kwargs):
        """
        Add a middleware to the application.
        """
        self._ensure_not_finalized()

        self.dispatch_request = middleware_factory(self.dispatch_request,
                                                   *args, **kwargs)

    def add_config_var(self, key, type, default):
        """
        Add a configuration variable to the application.
        """
        self._ensure_not_finalized()

        if key.count('/') > 1:
            raise ValueError('key might not have more than one slash')
        self.cfg.config_vars[key] = (type, default)



def make_app(setup_func, instance_dir=None, **kw):
    """Create an application instance.

    `setup_func`
        The callable used by the application to set itself up. This
        is the main entry point into the application.

    `instance_dir`
        The directory to use for instance-specific information

    `kw`
        See :class:`GlashammerApplication`
    """
    application = local('application')
    application = GlashammerApplication(setup_func,
                                        instance_dir, **kw)
    return application


