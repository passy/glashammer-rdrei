
from wtforms import Form, TextField
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
    db.Column('role', db.Integer)
)

roles = db.Table('roles', metadata,
    db.Column('role_id', db.Integer, primary_key=True),
    db.Column('name', db.String(30)),
)

class Role(object):
    pass

db.mapper(Role, roles)

class User(object):
    pass

db.mapper(User, users)


class UserForm(Form):

    email = TextField()
    name = TextField()

def register_view(req):
    form = UserForm(req.form)
    if req.method == 'POST':
        pass
    

def setup(app):
    # check the kind of auth we have
    app.add_url('/register', 'auth/register', register_view)
    app.add_data_func(init_data)

def init_data(engine):
    metadata.create_all(engine)
    admin_role = Role.objects.get(1)
    if admin_role is None:
        r = Role()
        r.name = 'admin'
        db.commit()


