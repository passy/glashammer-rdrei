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


import threading

from storm.locals import Storm, Store, Int, Unicode, create_database

from werkzeug.local import Local, LocalManager

from glashammer.bundle import Bundle


class StormCreator(object):

    @classmethod
    def _get_type_for_var(cls, col):
        name = col._name
        vtype = col._variable_class.__name__
        if vtype == 'IntVariable':
            if col._primary:
                vname = 'INTEGER PRIMARY KEY'
            else:
                vname = 'INTEGER'
        elif vtype == 'DateVariable':
            vname = 'DATE'
        elif vtype == 'UnicodeVariable':
            vname = 'VARCHAR'
        elif vtype == 'BoolVariable':
            vname = 'BOOL'
        elif vtype == 'FloatVariable':
            vname = 'FLOAT'
        elif vtype == 'TimeVariable':
            vname = 'TIME'
        else:
            raise TypeError('Unknown Type: %s (%s)' %
                (col._name, vtype))
        return '%s %s' % (name, vname)

    @classmethod
    def create_table(cls, store):
        cols = []
        for col, prop in cls._storm_columns.items():
            cols.append(cls._get_type_for_var(col))
        q = 'CREATE TABLE %s (%s)' % (cls.__storm_table__, ', '.join(cols))
        store.execute(q)
        print 'create', cls


class StormBase(Storm):

    id = Int(primary=True)


class StormCreatorBase(StormBase, StormCreator):

    """Self creating"""


def create_store(uri):
    return Store(create_database(uri))


class ThreadSafeStorePool(object):

    def __init__(self, local, uri):
        self.uri = uri

    def get(self):
        local = threading.local()
        try:
            return local.store
        except AttributeError:
            db = create_database(self.uri)
            local.store = Store(db)
            return local.store


class StormBundle(Bundle):

    def lifecycle(self):
        self.local = Local()
        self.local_manager = LocalManager([self.local])
        self.register_config('DB_URI')

    def finalise(self):
        self.store_pool = ThreadSafeStorePool(self.local,
                            self.site.config.get('DB_URI'))

    def get_store(self):
        return self.store_pool.get()

    def create_middleware(self, app):
        return self.local_manager.make_middleware(app)

    store = property(get_store)
