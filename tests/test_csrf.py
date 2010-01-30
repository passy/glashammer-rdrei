# -*- coding: utf-8 -*-
"""
tests.test_csrf
~~~~~~~~~~~~~~~

Nose tests for the csrf bundle.

:copyright: 2010, The Glashammer Authors
:license: MIT
"""

from werkzeug.test import Client
from glashammer.utils.wrappers import Response
from glashammer.application import make_app
from glashammer.bundles.csrf import setup_csrf_protection, require_csrf_token


def simple_view(req):
    """A simple view that does a simple output."""

    return Response("Hello World!")


@require_csrf_token
def protected_view(req):
    """A view that requires a cookie and post csrf value to match."""

    return Response("Secure.")


class TestCSRFBundle(object):

    def setup_app(self, app):
        """Adds the csrf bundle to the app."""
        app.add_url('/simple', 'simple', view=simple_view)
        app.add_url('/protected', 'protected', view=protected_view)
        app.add_setup(setup_csrf_protection)

    def setup(self):
        """Creates a testing environment."""

        self.app = make_app(self.setup_app, 'test_output')
        self.client = Client(self.app, Response)

    def _get_csrf_token(self):
        """I found no better way to get the cookie value than to iterate
        through the whole cookie jar."""
        for cookie in self.client.cookie_jar:
            if cookie.name == 'glashammer_csrf':
                return cookie.value

    def test_simple_view(self):
        """Test if simple views still work and provide the csrf cookie."""

        response = self.client.get('/simple')
        assert response.status_code == 200
        assert response.data == "Hello World!"

        csrf_value = self._get_csrf_token()

        assert csrf_value is not None, "No CSRF cookie has been found."

    def test_protected_view_fail(self):
        """Check if posting fails without a valid _csrf_token post value."""

        response = self.client.get('/protected')
        assert response.status_code == 403
        assert "CSRF protection validation failed" in response.data

    def test_protected_view(self):
        """Post something to the protected view and make sure that worked."""

        # Do an initial get request to get a fresh cookie
        self.client.get('/simple')

        response = self.client.post('/protected', data={
            '_csrf_token': self._get_csrf_token()})

        assert response.status_code == 200
        assert response.data == "Secure."
