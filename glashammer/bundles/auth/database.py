# -*- coding: utf-8 -*-
"""
    glashammer.models
    ~~~~~~~~~~~~~~~~~

    The core models and query helper functions.

    :copyright: 2007-2008 by Armin Ronacher, Pedro Algarvio.
    :license: GNU GPL.
"""
from math import ceil, log
from datetime import date, datetime, timedelta

#from textpress.utils import Pagination, gen_pwhash, check_pwhash, gen_slug, \
#     build_tag_uri
from glashammer.utils import get_app, url_for, gen_pwhash, gen_salt, \
    check_pwhash

from wtforms import Form, TextField

from glashammer.utils import render_response, sibpath
from glashammer.database import metadata, db


users = db.Table('users', metadata,
    db.Column('user_id', db.Integer, primary_key=True),
    db.Column('username', db.String(30)),
    db.Column('first_name', db.String(40)),
    db.Column('last_name', db.String(80)),
    db.Column('display_name', db.String(130)),
    db.Column('description', db.Text),
    db.Column('extra', db.PickleType),
    db.Column('pw_hash', db.String(70)),
    db.Column('email', db.String(250)),
    db.Column('role', db.Integer, default=4)
)

roles = db.Table('roles', metadata,
    db.Column('role_id', db.Integer, primary_key=True),
    db.Column('username', db.String(30)),
    db.Column('email', db.String(255)),
)

class Role(object):
    pass

db.mapper(Role, roles)


#: user rules
ROLE_ADMIN = 4
ROLE_EDITOR = 3
ROLE_AUTHOR = 2
ROLE_SUBSCRIBER = 1
ROLE_NOBODY = 0

class UserManager(db.DatabaseManager):
    """Add some extra query methods to the user object."""

    def get_nobody(self):
        return AnonymousUser()

    def filter_authors(self):
        return self.filter(User.role >= ROLE_AUTHOR)

    def get_authors(self):
        return self.filter_authors().all()


class User(object):
    """Represents an user.

    If you change something on this model, even default values, keep in mind
    that the websetup does not use this model to create the admin account
    because at that time the TextPress system is not yet ready. Also update
    the code in `textpress.websetup.WebSetup.start_setup`.
    """

    objects = UserManager()
    is_somebody = True

    def __init__(self, username=u'', password=None, email=u'', first_name=u'',
                 last_name=u'', description=u'', role=ROLE_SUBSCRIBER):
        self.username = username
        if password is not None:
            self.set_password(password)
        else:
            self.disable()
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.description = description
        self.extra = {}
        self._display_name = u'$nick'
        self.role = role

    @property
    def is_manager(self):
        return self.role >= ROLE_AUTHOR

    @property
    def role_as_string(self):
        """Human readable version of the role id."""
        from glashammer.utils import _
        if self.role == ROLE_ADMIN:
            return _('Administrator')
        elif self.role == ROLE_EDITOR:
            return _('Editor')
        elif self.role == ROLE_AUTHOR:
            return _('Author')
        elif self.role == ROLE_SUBSCRIBER:
            return _('Subscriber')
        return _('Nobody')

    def _set_display_name(self, value):
        self._display_name = value

    def _get_display_name(self):
        from string import Template
        return Template(self._display_name).safe_substitute(
            nick=self.username,
            first=self.first_name,
            last=self.last_name
        )

    display_name = property(_get_display_name, _set_display_name)

    def get_password(self):
        return None

    def set_password(self, password):
        self.pw_hash = gen_pwhash(password)

    password = property(get_password, set_password)

    def check_password(self, password):
        if self.pw_hash == '!':
            return False
        return check_pwhash(self.pw_hash, password)

    def disable(self):
        self.pw_hash = '!'

    def get_url_values(self):
        if self.role >= ROLE_AUTHOR:
            return 'blog/show_author', {
                'username': self.username
            }

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.username
        )


class AnonymousUser(User):
    """Fake model for anonymous users."""
    is_somebody = False
    display_name = 'Nobody'
    first_name = last_name = description = username = ''
    role = ROLE_NOBODY
    objects = UserManager()

    def __init__(self):
        pass

    def check_password(self, password):
        return False

db.mapper(User, users)

