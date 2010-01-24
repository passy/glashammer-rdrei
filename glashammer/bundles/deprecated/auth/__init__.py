# -*- coding: utf-8 -*-
"""
    glashammer.bundles.auth
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2008 by Glashammer Developers
    :license: MIT
"""
import os

from werkzeug.exceptions import NotFound

from wtforms import Form, TextField, PasswordField

from glashammer.utils import render_response, sibpath, emit_event, redirect, \
    get_app, url_for

from glashammer.bundles.sessions import setup_sessions, get_session

def get_username():
    session = get_session()
    app = get_app()
    return session.get(app.conf['auth/token_key'])

def get_user():
    pass

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

def auth_protected_view(f):
    """
    Decorator to only allow authorized users to access the view
    """
    def wrapped(*args, **kw):
        if get_app().conf['auth/token_key'] in get_session():
            return f(*args, **kw)
        else:
            return redirect(url_for('auth/login'))
    return wrapped



# Basic logging in view and forms

class UserForm(Form):

    username = TextField()
    password = PasswordField()


def view_login(request):
    """Show a login page."""
    error = None
    form = UserForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = form.username.data
            password = form.password.data
            if username and check_username_password(username, password):
                login(username)
                return redirect('/')

        error = ('Incorrect password.')

    return render_response('auth_login.jinja', error=error,
                           auth_form=form)

def view_logout(request):
    """Just logout and redirect to the login screen."""
    logout()
    return redirect(url_for('auth/login'))





def setup_auth(app, add_auth_views=True):
    """
    Setup the application to use auth.

    `add_auth_views`
        If True, the views for /login and /logout are created for you. This is
        the reference implementation that you may or may not want to replace.
    """

    app.add_setup(setup_sessions)
    app.add_config_var('auth/token_key', str, 'auth_session_key')
    app.add_template_searchpath(sibpath(__file__, 'templates'))


    if add_auth_views:
        app.add_url('/login', endpoint='auth/login', view=view_login)
        app.add_url('/logout', endpoint='auth/logout', view=view_logout)

setup_app = setup_auth

