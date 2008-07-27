import os

from werkzeug.exceptions import NotFound

from wtforms import Form, TextField, PasswordField

from glashammer.utils import render_response, sibpath, emit_event, redirect, \
    get_app, url_for

from glashammer.bundles.sessions import setup_sessions, get_session



class UserForm(Form):

    username = TextField()
    password = PasswordField()

def register_view(req):
    form = UserForm(req.form)
    if req.method == 'POST' and form.validate():
        u = User()
        form.auto_populate(u)
        u.password = 'ali'
        u.role = 4
        db.commit()
    return render_response('auth_register.html', form=form)

def check_username_password(username, password):
    tokens = emit_event('password-check', username, password)
    for token in tokens:
        #XXX only use the first token - maybe bad
        if token:
            return username

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



def do_login(request):
    """Show a login page."""
    #if request.user.is_somebody:
    #    return simple_redirect('admin/index')
    error = None
    username = ''
    #redirect = IntelligentRedirect()

    form = UserForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = form.username.data
            password = form.password.data
            if username:
                token = check_username_password(username, password)
                if token:
                    login(token)
                    return redirect('/')
        error = ('Incorrect password.')

    return render_response('auth_login.jinja', error=error,
                           auth_form=form,
                           username=username,
                           logged_out=request.values.get('logout') == 'yes',
                           hidden_redirect_field=redirect)

def do_logout(request):
    """Just logout and redirect to the login screen."""
    logout()
    return redirect(url_for('auth/login'))

def auth_protected_view(f):
    def wrapped(*args, **kw):
        if get_app().conf['auth/token_key'] in get_session():
            return f(*args, **kw)
        else:
            return redirect(url_for('auth/login'))
    return wrapped



def setup_auth(app):
    # check the kind of auth we have
    app.add_setup(setup_sessions)

    app.add_config_var('auth/token_key', str, 'auth_session_key')

    app.add_template_searchpath(sibpath(__file__, 'templates'))

    app.add_url('/register', 'auth/register', register_view)


    app.add_url('/login', endpoint='auth/login', view=do_login)
    app.add_url('/logout', endpoint='auth/logout', view=do_logout)



