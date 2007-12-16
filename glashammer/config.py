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

class MissingRequiredConfigOption(KeyError):
    """Raised when a required config option is missing"""


class ConfigOption(object):

    def __init__(self, name, default):
        self.name = name
        self.default = default


class ConfigBundle(Bundle):

    def create(self):
        self.options = {}

    def register(self, name, default=None):
        opt = ConfigOption(name, default)
        self.options[name] = opt

    def initialize(self):
        self.config = self.get_config()

    def get(self, name, default=None):
        return self.config.get(name, default)

    def get_default_config(self):
        conf = {}
        for k, v in self.options.items():
            if v.default is not None:
                conf[k] = v.default
        return conf

    def check_config(self, conf):
        for k in self.options:
            if k not in conf:
                raise MissingRequiredConfigOption(k)

    def get_config(self):
        conf = self.get_default_config()
        conf.update(self.site.site_config)
        self.check_config(conf)
        return conf


