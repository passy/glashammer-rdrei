

import os

from werkzeug import Request, Response, ClosingIterator, Local, LocalManager
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from glashammer.simpleconfig import SimpleConfig

from glashammer.templating import create_template_environment

from glashammer.utils import local, local_manager, EventManager, emit_event

from glashammer.database import db

DEFAULT_CONFIG = {'db_uri':'sqlite://'}

class GlashammerApplication(object):
    """WSGI Application"""

    def __init__(self, setup_func, instance_dir):
        # just for playing in the shell
        local.application = self

        self.finalized = False

        # Start the setup
        self.instance_dir = os.path.abspath(instance_dir)
        self.config_file = os.path.join(self.instance_dir, 'config.ini')

        if not os.path.exists(self.instance_dir):
            raise RunTimeError('Application instance director missing')

        self.conf = SimpleConfig(DEFAULT_CONFIG)

        if not os.path.exists(self.config_file):
            self.conf.dump_file(self.config_file)
        else:
            self.conf.merge(self.config_file)
        self.map = Map()
        self.views = {}
        self.events = EventManager(self)

        # Temporary variables for collecting setup information
        self._template_searchpaths = []
        self._setup_funcs = set()
        self._osetup_funcs = []
        self._data_funcs = set()
        self._odata_funcs = []

        # setup the application
        setup_func(self)

        # run the additional setup funcions
        for setup_func in self._osetup_funcs:
            setup_func(self)

        del self._setup_funcs

        # Now the database

        self.db_engine = db.create_engine(self.conf['db_uri'],
                                          convert_unicode=True)

        for data_func in self._odata_funcs:
            data_func(self.db_engine)

        del self._data_funcs



        # create the template environment
        self.template_env = create_template_environment(
            searchpaths=self._template_searchpaths
        )

        del self._template_searchpaths
        # finalize the setup
        self.finalized = True
        # create the template environment
        emit_event('app-setup')

    def __call__(self, environ, start_response):
        local.application = self
        local.adapter = adapter = self.map.bind_to_environ(environ)
        local.request = request = Request(environ)
        emit_event('app-request', request)
        try:
            endpoint, values = adapter.match()
            response = self.dispatch(request, endpoint, values)
        except HTTPException, e:
            response = e
        # cleanup
        emit_event('app-response', response)
        return ClosingIterator(response(environ, start_response),
                               [local_manager.cleanup])

    def dispatch(self, request, endpoint, values):
        view = self.views.get(endpoint)
        if view is None:
            return NotFound()
        else:
            return view(request, **values)

    def _prefinalize_only(f):
        def _decorated(self, *args, **kw):
            if self.finalized:
                raise RuntimeError('Already Finalized')
            return f(self, *args, **kw)
        return _decorated

    @_prefinalize_only
    def add_setup(self, setup_func):
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
    def add_template_searchpath(self, path):
        path = os.path.abspath(path)
        self._template_searchpaths.append(path)

    @_prefinalize_only
    def connect_event(self, event, callback, position='after'):
        """Connect an event to the current application."""
        return self.events.connect(event, callback, position)


def make_app(setup_func, instance_dir):
    application = local('application')
    application = GlashammerApplication(setup_func, instance_dir)
    application = local_manager.make_middleware(application)
    return application


