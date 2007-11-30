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

from unittest import TestCase

from glashammer.pastefixture import TestApp
from werkzeug.utils import create_environ


class TestController(TestCase):

    def __init__(self, *args, **kw):
        self.site = self.create_site()
        self.real_app = self.site.make_app()
        self.app = TestApp(self.real_app)
        self.dummy_environ = create_environ()
        self.map_adapter = self.site.routing.bind_to_environ(self.dummy_environ)
        TestCase.__init__(self, *args, **kw)

    def create_site(self):
        raise NotImplementedError

    def build_url(self, endpoint, argdict={}):
        return self.map_adapter.build(endpoint, argdict)

    def GET_ep(self, endpoint, argdict={}):
        return self.app.get(self.build_url(endpoint, argdict))

