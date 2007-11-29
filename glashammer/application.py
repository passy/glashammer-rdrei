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


from werkzeug.serving import run_simple
from werkzeug.routing import NotFound, RequestRedirect, Map
from werkzeug.utils import SharedDataMiddleware

from glashammer.utils import Request, NotFoundResponse, RedirectResponse
from glashammer.config import ConfigBundle
from glashammer.auth import AuthBundle
from glashammer.stormintegration import StormBundle
from glashammer.layout import LayoutBundle
from glashammer.jinjaintegration import create_jinja_environment
from glashammer.plugins import Registry
from glashammer.statics import StaticBundle
from glashammer.jinjaintegration import JinjaBundle
from glashammer.controller import ControllerBundle
from glashammer.routing import RoutingBundle
from glashammer.sessions import SessionBundle
from glashammer.features import FeatureBundle
from glashammer.processors import ProcessorBundle

import warnings


class GlashammerApplication(object):
    """WSGI Application"""

    def __init__(self, site):
        self.site = site
        self.controller_cache = {}

    def __call__(self, environ, start_response):
        url_adapter = self.site.routing.bind_to_environ(environ)
        req = Request(environ, url_adapter)

        # Request processors
        for proc in self.site.processors.list_request_processors():
            req = proc.process_request(req)
        try:
            endpoint, args = url_adapter.match(req.path)
            resp = self._get_response(environ, endpoint, args, req)
        except NotFound:
            resp = NotFoundResponse()
        except RequestRedirect, e:
            resp = RedirectResponse(e.new_url)

        # Response processors
        for proc in self.site.processors.list_response_processors():
            req = proc.process_response(req, resp)

        return resp(environ, start_response)

    def _get_response(self, environ, endpoint, args, req):
        endpoint_name, endpoint_method = endpoint.split('/', 1)
        try:
            controller = self.controller_cache[endpoint_name]
        except KeyError:
            controller = self._create_controller(endpoint_name)
            self.controller_cache[endpoint_name] = controller
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
            
    def _create_controller(self, endpoint_name):
        controller_type = self._get_controller(endpoint_name)
        if controller_type is not None:
            controller = controller_type(self.site)
            return controller

    def _get_controller(self, endpoint_name):
        return self.site.controller.get(endpoint_name)



class GlashammerSite(object):
    """
    Site. This is the boss that controls everything else, including the
    WSGI application
    """

    def __init__(self, site_config):
        self.bundles = []
        self.site_config = site_config
        # core bundles
        self.processors = self.register_bundle(ProcessorBundle)
        self.config = self.register_bundle(ConfigBundle)
        self.storm = self.register_bundle(StormBundle)
        self.controller = self.register_bundle(ControllerBundle)
        self.static = self.register_bundle(StaticBundle)
        self.jinja = self.register_bundle(JinjaBundle)
        self.routing = self.register_bundle(RoutingBundle)
        self.auth = self.register_bundle(AuthBundle)
        self.layout = self.register_bundle(LayoutBundle)
        self.session = self.register_bundle(SessionBundle)
        self.feature = self.register_bundle(FeatureBundle)

    def finalise(self):
        for bdl in self.bundles:
            bdl.finalise()

    def setup_site(self):
        self.finalise()
        for bdl in self.bundles:
            bdl.setup()

    def make_app(self):
        self.finalise()
        app = GlashammerApplication(self)
        return self.make_service_app(app)

    def make_service_app(self, app):
        for svc in self.bundles:
            try:
                app = svc.create_middleware(app)
            except NotImplementedError:
                pass
        return app

    def register_bundle(self, bundle_class):
        bdl = bundle_class(self)
        self.bundles.append(bdl)
        return bdl
        
    def run_debug_server(self, host='localhost', port=8080, autoreload=True):
        run_simple(host, port, self.make_app(), autoreload)


