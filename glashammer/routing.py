
from werkzeug.routing import Map, Rule
from glashammer.service import Service

class RoutingService(Service):

    def lifecycle(self):
        self.map = Map()

    def register(self, *rules):
        for rule in rules:
            self.map.add(rule)
    
    def bind_to_environ(self, environ):
        return self.map.bind_to_environ(environ)


