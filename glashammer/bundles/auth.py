# -*- coding: utf-8 -*-
"""
    glashammer.bundles.auth
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2008-2009 by Glashammer Developers
    :license: MIT
"""
import os

from glashammer.utils import (
    render_response, sibpath, emit_event, redirect,
    get_app, url_for
)

from glashammer.bundles.sessions import setup_sessions, get_session

def get_username():
    session = get_session()
    app = get_app()
    return session.get(app.conf['auth/token_key'])

def check_username_password(username, password):
    tokens = emit_event('password-check', username, password)
    if any(tokens):
        return username

def check_role(token, role_key):
    roles = emit_event('role-check', token, role_key)
    if any(roles):
        return True

def login(token):
    session = get_session()
    app = get_app()
    session[app.conf['auth/token_key']] = token

def logout():
    session = get_session()
    app = get_app()
    del session[app.conf['auth/token_key']]

def set_user_password(username, password):
    emit_event('password-change', username, gen_pwhash(password))

def setup_auth(app):
    """
    Setup the application to use auth.
    """

    app.add_setup(setup_sessions)
    app.add_config_var('auth/token_key', str, 'auth_session_key')


setup_app = setup_auth

