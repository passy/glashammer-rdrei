
"""
glashammer.utils.appliance
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2008-2009 Glashammer Developers
:license: MIT

The Glashammer Appliances.
"""

import sys, os

from werkzeug.routing import Rule, Submount, EndpointPrefix

from glashammer.utils import sibpath, render_response, url_for, redirect_to, \
    render_template


def expose(url, endpoint=None, **rule_kw):
    def view(f, endpoint=endpoint, rule_kw=rule_kw):
        f.url = url
        if endpoint is None:
            endpoint = f.func_name
        f.endpoint = endpoint
        f.rule_kw = rule_kw
        return f
    return view


class Appliance(object):
    """
    A mountable bundle of goodness.
    """
    target_prefix = ''

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
        self.name = self.endpoint_prefix
        self.module = sys.modules[self.__module__]

        if self.mountpoint_path is None:
            self.mountpoint_path = '/%s' % self.endpoint_prefix

    def configure(self, conf):
        for k in conf:
            if k in self.default_config:
                setattr(self, k, conf[k])

    def add_url(self, url, endpoint, view, **rule_kw):
        self._rules.append(Rule(url, endpoint=endpoint))

    def auto_add_urls(self):
        for rule in self._find_rules():
            self._rules.append(rule)

    def create_rule_factory(self):
        return EndpointPrefix(self.endpoint_prefix + '/', [
            Submount(self.mountpoint_path, self._rules)
        ])

    def setup(self, app):
        self.auto_add_urls()
        app.add_url_rule(self.create_rule_factory())
        app.add_views_controller(self.endpoint_prefix, self)
        app.add_template_searchpath(
            self.get_package_path(self.templates_path))
        app.add_shared(self.name, self.get_package_path(self.shared_path))
        app.add_setup(self.setup_appliance)
        print app._shared_exports

    def setup_appliance(self, app):
        pass

    @property
    def _module(self):
        return sys.modules[self.__module__]

    def get_package_path(self, path):
        return sibpath(self.module.__file__, path)

    def get_endpoint(self, endpoint_name):
        return '/'.join([self.endpoint_prefix, endpoint_name])

    def url_local(self, endpoint_name, **kw):
        return url_for(self.get_endpoint(endpoint_name), **kw)

    def url_shared(self, filename, **kw):
        return url_for('shared/%s' % self.name, filename=filename, **kw)

    def redirect_to(self, endpoint_name, **kw):
        return redirect_to(self.get_endpoint(endpoint_name), **kw)

    def render_template(self, template_name, **kw):
        kw['url_local'] = self.url_local
        kw['url_shared'] = self.url_shared
        return render_template(template_name, **kw)

    def render_response(self, template_name, **kw):
        kw['url_local'] = self.url_local
        kw['url_shared'] = self.url_shared
        return render_response(template_name, **kw)

    def _find_urls(self):
        for name in dir(self):
            attr = getattr(self, name)
            if hasattr(attr, 'url'):
                yield attr

    def _find_rules(self):
        for method in self._find_urls():
            yield Rule(method.url, endpoint=method.endpoint, **method.rule_kw)

    __call__ = setup


#XXX Just For Testing
class _JustForTestingAppliance(Appliance):
    @expose('/')
    def index(self, req):
        from glashammer.utils import Response
        return Response('hello')



