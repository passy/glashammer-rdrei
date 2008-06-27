

import os

from werkzeug import Request, Response, ClosingIterator, Local, LocalManager
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from gh.simpleconfig import SimpleConfig


local = Local()
local_manager = LocalManager([local])


def render_template(template_name, _stream=False, **context):
    #emit_event('before-render-template', template_name, _stream, context)
    tmpl = local.application.template_env.get_template(template_name)
    if _stream:
        return tmpl.stream(context)
    return tmpl.render(context)


def render_response(template_name, mimetype='text/html', **context):
    return Response(
        render_template(template_name, **context),
        mimetype=mimetype
    )


class GlashammerApplication(object):
    """WSGI Application"""

    def __init__(self, setup_func, instance_dir, config_name='gh.ini'):
        # just for playing in the shell
        local.application = self

        # Start the setup
        self.instance_dir = os.path.abspath(instance_dir)
        self.config_file = os.path.join(self.instance_dir, config_name)

        self.conf = SimpleConfig()
        self.map = Map()
        self.views = {}

        self._template_searchpaths = []

        # setup the application
        setup_func(self)

        self.template_env = Environment(
            loader=FileSystemLoader(self._template_searchpaths)
        )

        # finalize the setup

        # create the template environment


    def __call__(self, environ, start_response):
        local.application = self
        local.adapter = adapter = self.map.bind_to_environ(environ)
        local.request = request = Request(environ)
        try:
            endpoint, values = adapter.match()
            response = self.dispatch(request, endpoint, values)
        except HTTPException, e:
            response = e
        # cleanup
        return ClosingIterator(response(environ, start_response),
                               [local_manager.cleanup])


    def create_url_map(self):
        map = Map()
        map.add(Rule('/', endpoint='index'))
        map.add(Rule('/add', endpoint='add'))
        return map


    def dispatch(self, request, endpoint, values):
        view = self.views.get(endpoint)
        if view is None:
            return NotFound()
        else:
            return view(request, **values)


    def add_url_rule(self, url, endpoint, view=None, **kw):
        rule = Rule(url, endpoint=endpoint, **kw)
        if view is not None:
            self.views[endpoint] = view
        self.map.add(rule)

    def add_template_searchpath(self, path):
        path = os.path.abspath(path)
        self._template_searchpaths.append(path)



def make_app(setup_func, instance_dir, config_name='gh.ini'):
    application = local('application')
    application = GlashammerApplication(setup_func, instance_dir, config_name)
    application = local_manager.make_middleware(application)
    return application


def run_very_simple(app):
    from werkzeug import run_simple
    run_simple('localhost', 6060, app, use_reloader=True)


