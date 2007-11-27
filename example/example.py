"""
Hello World in Glashammer
"""

from glashammer.application import GlashammerSite
from glashammer.utils import Controller, Response, Service
from glashammer.routing import Rule
from glashammer.auth import UserPermission


# Controller
class HelloController(Controller):

    def hello(self, req):
        return self.create_template_response('hello.jinja')

    def byebye(self, req):
        UserPermission(self.site, self.user_id)
        return Response('bye bye')

    def session(self, req):
        self.session['foo'] = self.session.get('foo', 0) + 1
        return Response('You Clicked me: %s' % self.session['foo'])

# Service
class HelloService(Service):

    def lifecycle(self):
        # Register the controller explicitly
        self.register_controller('default', HelloController)
        # A statically served directory
        self.register_static_directory('/public', '/var/www')
        # A template directory
        self.register_template_directory('.')
        # some url rules
        self.register_url_rules(
            Rule('/', endpoint='default/hello'),
            Rule('/bye', endpoint='default/byebye'),
            Rule('/session', endpoint='default/session'),
        )
    

if __name__ == '__main__':
    site = GlashammerSite()
    # Register the service
    site.register_service(HelloService)
    # Start the debug server
    site.run_debug_server()



