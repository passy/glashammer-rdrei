
from unittest import TestCase

from glashammer.pastefixture import TestApp
from werkzeug.utils import create_environ


class TestController(TestCase):

    def __init__(self, *args, **kw):
        self.site = self.create_site()
        self.real_app = self.site.make_app()
        self.app = TestApp(self.real_app)
        self.dummy_environ = create_environ()
        self.map_adapter = self.site.routing_service.bind_to_environ(self.dummy_environ)
        TestCase.__init__(self, *args, **kw)

    def create_site(self):
        raise NotImplementedError

    def build_url(self, endpoint, argdict={}):
        return self.map_adapter.build(endpoint, argdict)

    def GET_ep(self, endpoint, argdict={}):
        return self.app.get(self.build_url(endpoint, argdict))

