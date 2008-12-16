# -*- coding: utf-8 -*-
"""
    glashammer.bundles.gae
    ~~~~~~~~~~~~~~~~~~~~~~

    Google Appengine integration

    :copyright: 2007 by Glashammer Developers
    :license: MIT
"""

import sys

from werkzeug.contrib.cache import MemcachedCache, BaseCache

from google.appengine.api import users, memcache
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

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



class GaeMemcachedCache(MemcachedCache):
    """A werkzeug memcached object for GAE"""

    def __init__(self, timeout=300):
        BaseCache.__init__(self, timeout)
        self._client = memcache.Client()


def setup_gae(app):
    app.connect_event('request-start', gae_local_processor)

def make_gae_app(setup_func):
    app = make_app(setup_func, '.')
    return app

# issue 772
sys_path = None
def fix_sys_path():
    global sys_path
    if sys_path is None:
        sys_path = list(sys.path)
    else:
        sys.path[:] = sys_path

def make_and_run_gae_app(setup_func):
    fix_sys_path()
    app = make_gae_app(setup_func)
    run_wsgi_app(app)


