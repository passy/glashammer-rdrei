# -*- coding: utf-8 -*-
"""
glashammer.bundles.middleware.csrf_protection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a simple middleware to secure against Cross Site Remote Forgery
attacks by setting cookies on every request and validate them on post
requests.

:copyright: 2010, The Glashammer Authors
:license: MIT
"""

from hashlib import sha1
from functools import wraps
from time import time
from glashammer.utils.wrappers import Request
from werkzeug.exceptions import Forbidden
import logging

log = logging.getLogger('glashammer.bundles.csrf')


class CSRFProtectionMiddleware(object):
    """
    Middleware that sets a random string to a cookie. This can be used
    to validate the the request comes from the expected origin.

    Use :func:`setup_csrf_protection` and don't use this directly.

    """

    def __init__(self, app, cookie_name):
        self.app = app
        self.cookie_name = cookie_name

        app.connect_event('response-start', self.set_cookie)

    def set_cookie(self, response):
        """Sets a unique string to the cookie."""
        if not hasattr(response, 'no_csrf_cookie'):
            response.set_cookie(self.cookie_name, self._generate_token())

    def _generate_token(self):
        """Generate a new random string based on time and secret set in the
        config."""
        return sha1("%s#%s" % (time(),
                               self.app.cfg['sessions/secret'])).hexdigest()


def setup_csrf_protection(app, cookie_name='glashammer_csrf'):
    """Sets up the csrf protection middleware.

    :param cookie_name: Cookie to store the secret key in. Remember that you
    have to create a new ``require_csrf_token`` decorator, if you change this
    value.
    """

    # In case the session bundle is not activated.
    app.add_config_var('sessions/secret', str, 'glashammer_secret')
    middleware = CSRFProtectionMiddleware(app, cookie_name)


def require_csrf_token_factory(form_var='_csrf_token',
                               cookie_var='glashammer_csrf',
                               exception_type=Forbidden):
    """Create a new ``require_csrf_token`` decorator based on the options
    submitted."""

    def get_request(args):
        """Tries to retrieve the request object from a list of arguments.
        Returns the first argument in the list that looks like a request
        object.
        This is used to make function-style views and method-style controllers
        both work.

        """

        for arg in args:
            if isinstance(arg, Request):
                return arg

        raise TypeError("No request object found in function call!")

    def require_csrf_token(func):
        """Raises a Forbidden by default if posted '_csrf_token' does
        not match the cookie value."""

        @wraps(func)
        def decorator(*args, **kwargs):
            req = get_request(args)

            if form_var not in req.form or \
               cookie_var not in req.cookies:
                log.info("CSRF-Protection failed. Either cookie or post "
                          "value not found!")
                raise exception_type("CSRF protection validation failed! "
                                     "Form data missing!")

            elif req.form[form_var] != req.cookies[cookie_var]:
                log.info("CSRF-Protection failed. Expected %s, got %s.",
                         req.cookies[cookie_var], req.form[form_var]);
                raise exception_type("CSRF protection validation failed! "
                                     "Form data invalid!")
            else:
                return func(*args, **kwargs)

        return decorator

    return require_csrf_token


# Default decorators.
require_csrf_token = require_csrf_token_factory()

__all__ = ('setup_csrf_protection', 'require_csrf_token',
           'require_csrf_token_factory')
