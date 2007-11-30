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


class Bundle(object):

    def __init__(self, site):
        self.site = site
        self.lifecycle()

    # Overridable bundle API

    def lifecycle(self):
        pass

    def finalise(self):
        pass

    def setup(self):
        """
        This is called when you first want to set up your application.

        Use it to create database tables and initial data.
        """
        pass

    def process_request(self, req):
        return req

    def process_response(self, resp, req):
        return resp

    def get_priority(self):
        return 100

    def create_middleware(self, app):
        raise NotImplementedError


    # Database Access
    def get_store(self):
        return self.site.storm.store

    store = property(get_store)

    # Registering activities for the bundle
    def register_static_directory(self, name, path):
        self.site.static.register(name, path)

    def register_url_rules(self, *rules):
        self.site.routing.register(*rules)

    def register_controller(self, name, controller):
        self.site.controller.register(name, controller)

    def register_template_directory(self, path):
        self.site.jinja.register(path)

    def register_config(self, name, default=None):
        self.site.config.register(name, default)

    def register_feature_provider(self, feature, provider):
        self.site.feature.register(feature, provider)

    def register_response_processor(self, processor):
        self.site.processors.register_response_processor(processor)

    def register_request_processor(self, processor):
        self.site.processors.register_request_processor(processor)

    # Listing features provided by the bundle
    def list_feature_providers(self, feature):
        return self.site.feature.list(feature)




