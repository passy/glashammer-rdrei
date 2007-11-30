# -*- coding: utf-8 -*-
#
# Copyright 2007 Glashammer Project
#
# The MIT License
#
# Copyright (c) <year> <copyright holders>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os

from werkzeug.wrappers import BaseRequest, BaseResponse
from glashammer.plugins import Registry


class Request(BaseRequest):
    """
    The concrete request object used in the WSGI application.
    It has some helper functions that can be used to build URLs.
    """
    charset = 'utf-8'

    def __init__(self, environ, url_adapter):
        BaseRequest.__init__(self, environ)
        self.url_adapter = url_adapter

    def url_for(self, endpoint, **values):
        """Create an URL to a given endpoint."""
        return self.url_adapter.build(endpoint, values)

    def external_url_for(self, endpoint, **values):
        """Create an external URL to a given endpoint."""
        return self.url_adapter.build(endpoint, values, True)


class Response(BaseResponse):
    """
    The concrete response object for the WSGI application.
    """
    charset = 'utf-8'


class RedirectResponse(Response):
    """
    A response object that redirects to a new URL.
    """

    def __init__(self, url, status=302):
        Response.__init__(self, 'page moved to %s' % url,
                          headers=[('Location', url)], status=status)


class NotFoundResponse(Response):
    """
    A response that represents a not existing resource.
    """

    def __init__(self):
        Response.__init__(self, '<h1>Page Not Found</h1>',
                          status=404, mimetype='text/html')


class TemplateResponse(Response):

    def __init__(self, site, template_name, template_kw, mimetype='text/html',
                 status=200, req=None,
                 controller=None, *args, **kw):
        self.site = site
        self.request = req
        self.controller = controller
        self.template = self.site.jinja.env.get_template(template_name)
        self.template_kw = template_kw
        Response.__init__(self, status=status, mimetype=mimetype, *args, **kw)

    def __call__(self, environ, start_response):
        self.map_adapter = self.site.routing.bind_to_environ(environ)
        self._update_template_kw()
        self.response = self.template.render(**self.template_kw)
        return Response.__call__(self, environ, start_response)

    def _update_template_kw(self):
        self.template_kw.update(dict(
            site = self.site,
            request=self.request,
            controller=self.controller,
            map_adapter=self.map_adapter,
        ))


class Prioritisable(object):

    def get_priority(self):
        return 100


# Stolen from twisted
def sibpath(path, sibling):
    """Return the path to a sibling of a file in the filesystem.

    This is useful in conjunction with the special __file__ attribute
    that Python provides for modules, so modules can load associated
    resource files.
    """
    return os.path.join(os.path.dirname(os.path.abspath(path)), sibling)

