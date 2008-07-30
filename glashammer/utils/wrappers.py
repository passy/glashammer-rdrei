# -*- coding: utf-8 -*-
"""
    glashammer.utils.wrappers
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2007-2008 by Armin Ronacher, Ali Afshar
    :license: MIT
"""
from werkzeug import run_simple, Request as wzRequest, Response as wzResponse, redirect

from glashammer.utils import local

# Template rendering

def render_template(template_name, _stream=False, **context):
    #emit_event('before-render-template', template_name, _stream, context)
    tmpl = local.application.template_env.get_template(template_name)
    if _stream:
        return tmpl.stream(context)
    return tmpl.render(context)

def render_response(template_name, mimetype='text/html', **context):
    """Render a template and return a response instance.

    `template_name` The name of the template to use, this can include a relative
    path to the template from the searchpath directory.

    `mimetype` The mimetype for the response.

    `context` Key worded context variables for the template. These variables are
    passed into the template namespace.
    """
    return Response(
        render_template(template_name, **context),
        mimetype=mimetype
    )


class Response(wzResponse):
    default_mimetype = 'text/html'


class Request(wzRequest):
    """The used request class."""

    def __init__(self, app, environ):
        wzRequest.__init__(self, environ)
        self.app = app


