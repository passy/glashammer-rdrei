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


from glashammer.bundle import Bundle
from glashammer.utils import TemplateResponse


class ControllerBundle(Bundle):

    def create(self):
        self.controllers = {}

    def register(self, name, controller):
        self.controllers[name] = controller

    def get(self, name):
        return self.controllers.get(name)


class Controller(object):

    def __init__(self, site,):
        self.site = site

    def __before__(self, req, *args):
        pass

    def __after__(self, req, *args):
        pass

    def create_template_response(self, req, name, **kw):
        return TemplateResponse(self.site, name, kw, req=req, controller=self)

    # XXX May not be the right place for this
    def list_feature_providers(self, feature):
        return self.site.features.list_feature_providers(feature)


