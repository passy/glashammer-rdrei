# -*- coding: utf-8 -*-
"""
    glashammer.bundles.gae
    ~~~~~~~~~~~~~~~~~~~~~~

    Google Appengine integration

    :copyright: 2007 by Glashammer Developers
    :license: MIT
"""

from wsgiref.handlers import CGIHandler

from werkzeug.contrib.cache import MemcachedCache, BaseCache

from google.appengine.api import users, memcache
from google.appengine.ext import db

from glashammer.utils import local, get_request, redirect
from glashammer.application import make_app


def get_gae_user():
    return local.gae_user


def get_gae_cache():
    return local.gae_cache


def gae_local_processor(req):
    user = users.get_current_user()
    local.gae_user = user
    cache = GaeMemcachedCache()
    local.gae_cache = cache


def gae_user_only_view(f):
    def wrapped(req, **kw):
        if local.gae_user is None:
            return redirect_gae_login_url()
        else:
            return f(req, **kw)
    return wrapped


def gae_admin_only_view(f):
    def wrapped(req, **kw):
        if not users.is_current_user_admin():
            return redirect_gae_login_url()
        else:
            return f(req, **kw)
    return wrapped


def redirect_gae_login_url():
    req = get_request()
    return redirect(users.create_login_url(req.url))


from google.appengine.api import memcache

class GaeMemcachedCache(MemcachedCache):
    """A werkzeug memcached object for GAE"""

    def __init__(self, timeout=300):
        BaseCache.__init__(self, timeout)
        self._client = memcache.Client()


def setup_gae(app, cache_manage_url=None):
    app.connect_event('request-start', gae_local_processor)

    if cache_url


def make_gae_app(setup_func):
    app = make_app(setup_func, '.')
    return app


def make_and_run_gae_app(setup_func):
    app = make_gae_app(setup_func)
    CGIHandler().run(app)


