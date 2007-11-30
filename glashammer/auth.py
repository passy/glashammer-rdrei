# -*- coding: utf-8 -*-
#
# Copyright 2007 Glashammer Project
#
# The MIT License
#
# Copyright (c) <year> <copyright holders>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""
Really simple auth.
"""

import os

from glashammer.bundle import Bundle
from glashammer.controller import Controller
from glashammer.utils import Response, RedirectResponse, Request
from glashammer.stormintegration import StormBase, StormCreatorBase, Unicode

from werkzeug.routing import RequestRedirect, Rule

class NotAuthenticatedError(Exception):
    pass

class NotAuthorizedError(Exception):
    pass

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'auth_templates')


class AuthController(Controller):

    def login(self, req):
        if req.method == 'POST':
            redirect = req.form.get('login_redirect_back_to', '/')
            username = req.form.get('username')
            password = req.form.get('password')
            if not (username and password):
                return self._login_failure(req, redirect)
            user = self.site.storm.store.find(User, username=username,
                                        password=password).any()
            if user is None:
                return self._login_failure(req, redirect)
            else:
                req.session['user_id'] = username
                return RedirectResponse(redirect)
        else:
            redirect_back_to = req.args.get('attempted_page', '')
            return self.create_template_response(req, 'loginform.jinja',
                redirect_back_to = redirect_back_to,
            )

    def _login_failure(self, req, redirect):
        return RedirectResponse(req.url_for('auth/login',
                                attempted_page=redirect))


    def logout(self, req):
        redirect = req.args.get('logout_redirect_back_to', '/')
        req.session['user_id'] = 0
        return RedirectResponse(redirect)

#XXX Try to replace with pre-processing
class AuthMiddleware(object):

    def __init__(self, app, site):
        self.app = app
        self.site = site

    def __call__(self, environ, start_response):
        session = environ['werkzeug.session']
        environ['glashammer.user_id'] = session.get('user_id')
        try:
            return self.app(environ, start_response)
        except NotAuthenticatedError:
            map_adapter = self.site.routing.bind_to_environ(environ)
            req = Request(environ, map_adapter)
            resp = RedirectResponse(
                map_adapter.build('auth/login',
                    dict(attempted_page=req.url))
                )
            return resp(environ, start_response)
        except NotAuthorizedError:
            return Response('Forbidden', status=403)(environ, start_response)
        

class Permission(object):

    def __call__(self, user_id):
        raise NotImplementedError


class PublicPermission(object):

    def __call__(self, site, user_id):
        return True


class UserPermission(Permission):

    def __init__(self, site, user_id):
        if not user_id:
            raise NotAuthenticatedError


class AdminPermission(UserPermission):

    def __call__(self, site, user_id):
        UserPermission.__call__(self, site, user_id)
        if user_id == 'hoo':
            return True
        else:
            raise NotAuthorizedError





class User(StormCreatorBase):

    __storm_table__ = 'user'

    username = Unicode()
    password = Unicode()


class AuthBundle(Bundle):

    def lifecycle(self):
        self.set_user_class(User, User.create_table)
        self.user_class_setup = User.create_table
        self.register_controller('auth', AuthController)
        self.register_url_rules(
            Rule('/login', endpoint='auth/login'),
            Rule('/logout', endpoint='auth/logout'),
        )
        self.register_template_directory(TEMPLATE_PATH)

    def setup(self):
        # XXX Move this out into a setupt thing
        store = self.store
        try:
            User.create_table(store)
            store.commit()
        except:
            raise
            pass
        if store.find(User).any() is None:
            u = User()
            u.username = u'ali'
            u.password = u'ali'
            store.add(u)
            store.commit()

    def create_middleware(self, app):
        return AuthMiddleware(app, self.site)

    def setup(self):
        pass

    def set_user_class(self, user_class, setup_callable):
        self.user_class = user_class
        self.user_class_setup = setup_callable
