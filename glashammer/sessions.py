
from glashammer.service import Service

from werkzeug.contrib.sessions import SessionMiddleware, FilesystemSessionStore

class SessionService(Service):

    def create_middleware(self, app):
        return SessionMiddleware(app, FilesystemSessionStore('.'))
