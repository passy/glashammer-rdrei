"""
Glashammer Session handling.
"""
from glashammer.bundle import Bundle

from werkzeug.contrib.sessions import SessionMiddleware, FilesystemSessionStore

class SessionBundle(Bundle):

    def create_middleware(self, app):
        return SessionMiddleware(app, FilesystemSessionStore('.'))
