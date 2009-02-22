# -*- coding: utf-8 -*-
"""
    glashammer.bundles.sqlalchdb
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 200-2009 by Ali Afshar
    :license: MIT
"""


import os

from sqlalchemy import create_engine, orm, MetaData, Table, Column, types

from glashammer.utils import get_app
from glashammer.utils.local import local, local_manager
from glashammer.utils.config import config_overriding_val
from glashammer.utils.json import JsonRestService

# a new scoped session
session = orm.scoped_session(lambda: orm.create_session(
                             local.application.sqla_db_engine,
                             autoflush=True, autocommit=False),
                             local_manager.get_ident)

metadata = MetaData()

mapper = orm.mapper




def get_engine():
    """Get the SQLA DB Engine"""
    return get_app().sqla_db_engine


def data_init(app):
    metadata.create_all()


def cleanup_sqla_session(arg):
    session.remove()


def setup_sqlalchdb(app, default_uri=None):
    default = 'sqlite:///%s' % os.path.join(app.instance_dir, 'gh.sqlite')
    db_uri = config_overriding_val(app, default, default_uri, 'db.uri', str)
    app.connect_event('response-end', cleanup_sqla_session)
    app.connect_event('app-setup', cleanup_sqla_session)
    app.sqla_db_engine = create_engine(db_uri)
    metadata.bind = app.sqla_db_engine
    app.add_data_func(data_init)


