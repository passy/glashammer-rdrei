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
from glashammer.plugins import Registry


class GlashammerSite(object):
    """
    Base class so we can override a few things while testing.
    Some common places:
        self.confg      Config Framework(has to provide find)
        self.routing    Routing Framework(has to provide add)
        self.static     Static File Serving Framework(has to provide add_static_path)
    """

    def __init__(self, site_config):
        self.bundles = []
        self.features = Registry()
        self.site_config = site_config
        self.create_bundles()
        self.initialize_bundles()
    
    def register_feature(self, feature, provider):
        self.features.register_feature(feature, provider)
    
    def require_feature(self, feature):
        return self.feature.list_feature_providers(feature)
    
    def create_bundles(self):
        """
        This is the place where you should register the bundles you want to use
        OVERRIDE THIS!
        """
        raise 'RTFM!'
    
    def initialize_bundles(self):
        """
        Bring up all registered bundles
        """
        for bdl in self.bundles:
            bdl.initialize()

    def register_bundle(self, bundle_class):
        """
        Register a bundle with the site.

        The bundle will be registered and instantiated. When instantiated, it
        will run through its lifecycle, and register the required activities
        with the site.
        """
        bdl = bundle_class(self)
        self.bundles.append(bdl)
        return bdl
    
    def require_config(self, config_option, default=None):
        """ require a configuration option """
        return self.config.find(config_option, default)
    
    def setup_bundles(self):
        """ Setup up everything for the bundles """
        for bdl in self.bundles:
            bdl.setup()
