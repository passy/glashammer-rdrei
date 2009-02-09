# -*- coding: utf-8 -*-
"""
    glashammer.bundles.sessions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2007 by Armin Ronacher, Glashammer Developers
    :license: MIT
"""
from werkzeug.contrib.securecookie import SecureCookie
from glashammer.utils import local, get_app, get_request

def get_session():
    return local.session

def tag_session(req):
    app = get_app()
    cookie_name = app.conf['sessions/cookie_name']
    session = SecureCookie.load_cookie(req, cookie_name,
                                           app.conf['sessions/secret'])
    local.session = session

def cleanup_sessions(response):
    # save the session
    app = get_app()
    session = get_session()
    if session.should_save:
        cookie_name = app.conf['sessions/cookie_name']
        if session.get('pmt'):
            max_age = 60 * 60 * 24 * 31
            expires = time() + max_age
        else:
            max_age = expires = None
        session.save_cookie(response, cookie_name, max_age=max_age,
                            expires=expires, session_expires=expires)

def setup_sessions(app):
    app.add_config_var('sessions/cookie_name', str, 'glashammer_session')
    app.add_config_var('sessions/secret', str, 'glashammer_secret')

    app.connect_event('request-start', tag_session)
    app.connect_event('response-start', cleanup_sessions)

    app.add_template_global('session', local('session'))

setup_app = setup_sessions

