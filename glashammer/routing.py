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

from werkzeug.routing import Map
from glashammer.bundle import Bundle

class RoutingBundle(Bundle):
    def create(self):
        self.map = Map()
    
    def initialize(self):
        # load some config options for routing
        if self.site.require_config('routing.default_subdomain', None):
            self.map.default_subdomain = self.site.require_config('routing.default_subdomain')
        if self.site.require_config('routing.charset', None):
            self.map.charset = self.site.require_config('routing.charset')
        if self.site.require_config('routing.strict_slashes', None):
            self.map.strict_slashes = self.site.require_config('routing.strict_slashes')
        if self.site.require_config('routing.redirect_defaults', None):
            self.map.redirect_defaults = self.site.require_config('routing.redirect_defaults')
        # load additional converters
        if self.site.require_feature('routing.converters'):
            self.map.converters.update(self.site.require_feature('routing.converters'))
        
    def register(self, *rules):
        for rule in rules:
            self.map.add(rule)
    
    def bind_to_environ(self, env):
        return self.map.bind_to_environ(env)
