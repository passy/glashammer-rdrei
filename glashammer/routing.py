
from werkzeug.routing import Map
from glashammer.bundle import Bundle

class RoutingBundle(Bundle):

    def lifecycle(self):
        self.map = Map()

    def register(self, *rules):
        for rule in rules:
            self.map.add(rule)
    
    def bind_to_environ(self, environ):
        return self.map.bind_to_environ(environ)


