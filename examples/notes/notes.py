
from os.path import dirname

from glashammer.application import make_app
from glashammer.utils import run_very_simple, render_response
from glashammer.bundles.sqlalchdb import metadata, get_engine, \
        setup_sqlalchdb, mapper, Table, Column, types, session

FOLDER = dirname(__file__)

def index_view(req):
    return render_response('notes_index.jinja',
        notes=session.query(Note).order_by(Note.id))

def add_view(req):
    # validate form
    title = req.form.get('title', 'kT')
    text = req.form.get('text')
    prio = req.form.get('importance')
    if not text:
        text = "kT"
    note = Note(title, text, prio)
    session.add(note)
    session.commit()
    return render_response('notes_success.jinja')

def edit_view(req, nid):
    # find note
    note = session.query(Note).get(nid)
    # TODO: check if note exists
    return render_response('notes_edit.jinja', note=note)

def edit_submit_view(req, nid):
    # find note
    note = session.query(Note).get(nid)
    # TODO: check if note exists
    note.title = req.form.get('title')
    note.note = req.form.get('text')
    note.importance = req.form.get('importance')
    session.add(note)
    session.commit()
    return render_response('notes_success.jinja')

# The SQLA tables
notes = Table('notes', metadata,
    Column('id', types.Integer, primary_key=True),
    Column('title', types.Unicode),
    Column('note', types.Unicode),
    Column('importance', types.Unicode)
)

# The ORM mapped class
class Note(object):
    """ Represents a note """
    def __init__(self, title, text, importance=None):
        self.title = title
        self.note = text
        self.importance = importance

# Make a mapper which gives you the objects manager
mapper(Note, notes)

def setup(app):
    # Use the sqlalchdb bundle
    app.add_setup(setup_sqlalchdb)

    # Function to be run during data setup phase
    app.add_data_func(init_data)

    # Add the template searchpath
    app.add_template_searchpath(FOLDER)

    # Urls
    app.add_url('/', 'example/index', view=index_view)
    app.add_url('/add', 'example/add', view=add_view)
    app.add_url('/edit/<int:nid>', 'example/edit', view=edit_view)
    app.add_url('/edit/<int:nid>/submit', 'example/edit_submit', view=edit_submit_view)


def init_data(app):
    engine = get_engine()
    metadata.create_all(engine)

# Used by gh-admin
def create_app():
    return make_app(setup, FOLDER)

if __name__ == '__main__':
    app = create_app()
    run_very_simple(app)


