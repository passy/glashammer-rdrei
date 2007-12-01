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
from glashammer.utils import Prioritisable
from glashammer.plugins import Registry


class RequestProcessor(Prioritisable):

    def process_request(self, req):
        return req


class ResponseProcessor(Prioritisable):

    def process_response(self, req, resp):
        return resp


class ProcessorBundle(Bundle):

    def lifecycle(self):
        self.registry = Registry()

    def register_request_processor(self, processor):
        self.registry.register_feature(RequestProcessor, processor)

    def register_response_processor(self, processor):
        self.registry.register_feature(ResponseProcessor, processor)

    def _list_processors(self, processor_type):
        procs = self.registry.list_feature_providers(processor_type)
        procs.sort(self._priority_sort_func)
        return procs

    def _priority_sort_func(self, p1, p2):
        return cmp(p1.get_priority(), p2.get_priority())

    def list_request_processors(self):
        return self._list_processors(RequestProcessor)

    def list_response_processors(self):
        return self._list_processors(ResponseProcessor)


