# -*- coding: utf-8 -*-
from os.path import dirname

from storm.locals import *
from werkzeug import redirect
from wtforms import Form, TextField

from glashammer.application import make_app
from glashammer.utils import run_very_simple, sibpath, render_response

from glashammer.bundles.stormdb import setup_stormdb, get_store

TEMPLATES_DIRECTORY = sibpath(__file__, 'templates')
SHARED_DIRECTORY = sibpath(__file__, 'shared')

class Person(object):
    __storm_table__ = "person"
    id = Int(primary=True)
    name = Unicode()

class PersonForm(Form):
    name = TextField()

def main_view(req):
    s = get_store()
    return render_response('index.jinja',
        persons=s.find(Person).order_by('name'))

def save_view(req):
    form = PersonForm(req.form)
    if req.method == 'POST' and form.validate():
        store = get_store()
        p = Person()
        form.auto_populate(p)
        store.add(p)
        store.commit()
    return redirect('/')


# Main application setup
def setup(app):
    app.add_template_searchpath(TEMPLATES_DIRECTORY)
    app.add_shared('main', SHARED_DIRECTORY)
    app.add_url('/', 'person/index', view=main_view)
    app.add_url('/save', 'person/save', view=save_view)
    app.add_setup(setup_stormdb)


# Hook for gh-admin
def create_app():
    app =  make_app(setup, dirname(__file__))
    return app


def init_app():
    app = create_app()
    store = get_store()
    store.execute("CREATE TABLE person "
                  "(id INTEGER PRIMARY KEY, name VARCHAR)")
    store.commit()
    store.close()



if __name__ == '__main__':
    #app = create_app()
    #run_very_simple(app)
    init_app()

