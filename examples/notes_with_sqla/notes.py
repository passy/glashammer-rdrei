from os.path import dirname, join

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, \
                       String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, scoped_session
from wtforms import Form, TextField, TextAreaField, validators
from glashammer.application import make_app
from glashammer.utils import local, local_manager, get_app, redirect, \
    url_for, run_very_simple, render_response, Response


FOLDER = dirname(__file__)

Base = declarative_base()
metadata = Base.metadata
db = scoped_session(lambda: create_session(local.application.sqla_db_engine,
                    autocommit=False), local_manager.get_ident)


# Table, Class and Mapper - declarative style
class Note(Base):
    """ Represents a note """
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    title = Column(String(150))
    note = Column(Text)
    importance = Column(String(20))

    def __init__(self, title, text, importance=None):
        self.title = title
        self.note = text
        self.importance = importance


# The form
class NotesForm(Form):
    """Add/edit form for notes"""
    title = TextField(u'Title:', [validators.length(min=4, max=150)])
    note = TextAreaField(u'Note:', [validators.length(min=4, max=500)])
    importance = TextField(u'Importance:')


# The views
def index_view(req):
    notes = db.query(Note).order_by(Note.id.desc()).all()
    form = NotesForm(req.form)
    return render_response('notes_index.jinja', notes=notes, form=form)

def add_edit_view(req, nid=None):
    if nid is None:
        form = NotesForm(req.form)
        # Validate form
        if req.method == 'POST' and form.validate():
            # No validation errors, save note and redirect to success page
            note = Note(
                        req.form.get('title'),
                        req.form.get('note'),
                        req.form.get('importance')
                        )
            db.add(note)
            db.commit()
            return redirect(url_for('example/success'))
        return render_response('notes_add.jinja', form=form)
    else:
        # Find note
        note = db.query(Note).get(nid)
        # Check if note exists
        if note is None:
            return Response('Not Found', status=404)
        # Form with values
        form = NotesForm(req.form,
                        title = note.title,
                        note = note.note,
                        importance = note.importance
                        )
        # Validate form
        if req.method == 'POST' and form.validate():
            # No validation errors, update note and redirect to success page
            note.title = req.form.get('title')
            note.note = req.form.get('note')
            note.importance = req.form.get('importance')
            db.add(note)
            db.commit()
            return redirect(url_for('example/success'))
        return render_response('notes_edit.jinja', note=note, form=form)

def add_success_view(req):
    return render_response('notes_success.jinja')


# Setup
def _get_default_db_uri(app):
    db_file = join(app.instance_dir, 'gh.sqlite')
    return 'sqlite:///' + db_file

def setup(app):
    # Setting up our database
    app.add_config_var('sqla_db_uri', str, _get_default_db_uri(app))
    app.sqla_db_engine = create_engine(app.cfg['sqla_db_uri'],
                                          convert_unicode=True)
    metadata.bind = app.sqla_db_engine

    # Function to be run during data setup phase
    app.add_data_func(init_data)

    # Add the template searchpath
    app.add_template_searchpath(FOLDER)

    # Add bundles
    from glashammer.bundles.htmlhelpers import setup_htmlhelpers
    app.add_setup(setup_htmlhelpers)

    # Urls
    app.add_url('/', 'example/index', view=index_view)
    app.add_url('/add', 'example/add', view=add_edit_view)
    app.add_url('/add/success', 'example/success', view=add_success_view)
    app.add_url('/edit/<int:nid>', 'example/edit', view=add_edit_view)
    # Static files
    app.add_shared('files', join(FOLDER, 'static'))

def init_data(app):
    engine = get_app().sqla_db_engine
    metadata.create_all(engine)

# Used by gh-admin
def create_app():
    return make_app(setup, FOLDER)

if __name__ == '__main__':
    app = create_app()
    run_very_simple(app)
