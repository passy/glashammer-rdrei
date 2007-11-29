

from werkzeug.utils import SharedDataMiddleware
from glashammer.service import Service



class StaticService(Service):
    """A core service for handling static files"""
    def __init__(self, site):
        Service.__init__(self, site)
        self.static_directories = {}

    def register(self, name, path):
        self.static_directories[name] = path

    def create_middleware(self, app):
        static_map = dict(self.static_directories)
        app = SharedDataMiddleware(app, static_map)
        app.site = self
        return app
        
