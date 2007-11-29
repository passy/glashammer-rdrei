"""
Hello World in Glashammer
"""

import os

from glashammer import GlashammerSite, Response, Service, Controller, \
    Rule, UserPermission, EndpointLink


# Controller
class HelloController(Controller):

    def hello(self, req):
        return self.create_template_response('hello.jinja')

    def byebye(self, req):
        UserPermission(self.site, self.user_id)
        return Response('bye bye')

    def sess(self, req):
        self.session['foo'] = self.session.get('foo', 0) + 1
        return self.create_template_response('sitebase.jinja',
            content='You Clicked me: %s times' % self.session['foo'])

# Service
class HelloService(Service):

    def lifecycle(self):
        # Register the controller explicitly
        self.register_controller('default', HelloController)
        # A statically served directory
        self.register_static_directory('/public', '/var/www')
        # A template directory
        self.register_template_directory(os.path.dirname(__file__))
        # some url rules
        self.register_url_rules(
            Rule('/', endpoint='default/hello'),
            Rule('/bye', endpoint='default/byebye'),
            Rule('/session', endpoint='default/sess'),
        )
        self.register_feature_provider('navigation-item',
                EndpointLink('Session', 'default/sess'))
        self.register_feature_provider('navigation-item',
                EndpointLink('Logout', 'auth/logout'))
    

from glashammer.testing import TestController


class TestHelloController(TestController):

    def test_hello(self):
        res = self.GET_ep('default/hello')
        assert res.status == 200, 'Non 200 Status'
        assert 'Hello World' in res.normal_body

    def test_bye(self):
        res = self.GET_ep('default/byebye')
        assert res.status == 302, 'Not redirected to login'

    def test_session(self):
        res = self.GET_ep('default/sess')
        r1 = int(res.normal_body.split(':')[-1].strip())
        res = self.GET_ep('default/sess')
        r2 = int(res.normal_body.split(':')[-1].strip())
        assert r2 - r1 == 1

    def create_site(self):
        site = GlashammerSite()
        site.register_service(HelloService)
        return site


if __name__ == '__main__':
    site = GlashammerSite()
    # Register the service
    site.register_service(HelloService)
    # Start the debug server
    site.run_debug_server()



