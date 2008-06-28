
from os.path import dirname

from glashammer import make_app, run_very_simple, render_response
from glashammer.database import metadata, db
from glashammer.bundles.auth import setup as setup_auth, User
from glashammer.bundles.admin import setup as setup_admin

FOLDER = dirname(__file__)

def index_view(req):
    return render_response('hello.jinja')

def setup(app):
    app.add_url('/', 'example/hello', view=index_view)
    app.add_template_searchpath(FOLDER)
    app.add_setup(setup_admin),
    app.add_data_func(init_data)
    app.set_layout_template('hello.jinja')

class UserExtra(object):
    pass

def init_data(engine):
    users_extra = db.Table('users_extra', metadata,
        db.Column('user_extra_id', db.Integer, primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
        db.Column('notes', db.Unicode),
    )
    db.mapper(UserExtra, users_extra, properties={'user': db.relation(User)})
    metadata.create_all(engine)



if __name__ == '__main__':
    app = make_app(setup, FOLDER)
    run_very_simple(app)


