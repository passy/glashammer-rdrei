
"""
glashammer.utils.appliance
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2008-2009 Glashammer Developers
:license: MIT

The Glashammer Application.
"""

import sys, os

from werkzeug.routing import Rule, Submount, EndpointPrefix


def expose(url, default=None):
    def view(f):
        return f
    return view


class Appliance(object):
    """
    A mountable bundle of goodness.
    """
    target_prefix = 'view_'

    default_config = {
        'mountpoint_path': None,
        'endpoint_prefix': None,
        'templates_path': 'templates',
        'shared_path': 'shared'
    }

    def __init__(self, **conf):
        # I really hate crap like this, but functionality will fail if this
        # isn't in the right place. If you don't want this strict structure,
        # you don't want an Appliance.
        if self.__class__ is Appliance:
            raise ValueError('Appliance is strictly abstract.')
        self._rules = []
        self.configure(self.default_config)
        self.configure(conf)

        if self.endpoint_prefix is None:
            # I hat this crap too, but what are you going to do
            self.endpoint_prefix = self.__class__.__name__.lower()

        if self.mountpoint_path is None:
            self.mountpoint_path = '/%s' % self.endpoint_prefix


    def configure(self, conf):
        for k in conf:
            if k in self.default_config:
                setattr(self, k, conf[k])

    def add_url(self, url, endpoint, view):
        self._rules.append(Rule(url, endpoint=endpoint))

    def create_rule_factory(self):
        return EndpointPrefix(self.endpoint_prefix + '/', [
            Submount(self.mountpoint_path, self._rules)
        ])

    def setup(self, app):
        app.add_url_rule(self.create_rule_factory())
        app.add_views_controller(self.endpoint_prefix, self)
        app.add_template_searchpath(
            self.get_package_path(self.templates_path))
        app.add_shared(self.name, self.get_package_path(self.shared_path))

    @property
    def name(self):
        return self.__module__

    @property
    def module(self):
        return sys.modules[self.name]

    def get_package_path(self, path):
        return os.path.join(sys.modules[self.__module__].__file__, path)

    __call__ = setup



