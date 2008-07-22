import os

from wtforms import Form, TextField

from glashammer.utils import render_response, sibpath
from glashammer.bundles.sqladb import metadata, db

from database import User


class UserForm(Form):

    email = TextField()
    username = TextField()

def register_view(req):
    form = UserForm(req.form)
    if req.method == 'POST' and form.validate():
        u = User()
        form.auto_populate(u)
        u.password = 'ali'
        u.role = 4
        db.commit()
    return render_response('auth_register.html', form=form)
    

def setup(app):
    # check the kind of auth we have
    app.add_template_searchpath(sibpath(__file__, 'templates'))

    app.add_url('/register', 'auth/register', register_view)

    app.add_data_func(init_data)

def init_data(engine):
    metadata.create_all(engine)


