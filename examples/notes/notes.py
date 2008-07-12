
from os.path import dirname

from glashammer import make_app, run_very_simple, render_response
from glashammer.database import metadata, db

FOLDER = dirname(__file__)

def index_view(req):
    return render_response('notes_index.jinja', notes=Note.objects.order_by(Note.id))

def add_view(req):
    # validate form
    title = req.form.get('title', 'kT')
    text = req.form.get('text')
    prio = req.form.get('importance')
    if not text:
        text = "kT"
    note = Note(title, text, prio)
    db.commit()
    return render_response('notes_success.jinja')

def edit_view(req, nid):
    # find note
    note = Note.objects.get(nid)
    # TODO: check if note exists
    return render_response('notes_edit.jinja', note=note)

def edit_submit_view(req, nid):
    # find note
    note = Note.objects.get(nid)
    # TODO: check if note exists
    note.title = req.form.get('title')
    note.note = req.form.get('text')
    note.importance = req.form.get('importance')
    db.commit()
    return render_response('notes_success.jinja')

class Note(object):
    """ Represents a note """
    def __init__(self, title, text, importance=None):
        self.title = title
        self.note = text
        self.importance = importance

def setup(app):
    from glashammer.bundles.sqladb import setup_sqladb
    app.add_setup(setup_sqladb)

    app.add_url('/', 'example/index', view=index_view)
    app.add_url('/add', 'example/add', view=add_view)
    app.add_url('/edit/<int:nid>', 'example/edit', view=edit_view)
    app.add_url('/edit/<int:nid>/submit', 'example/edit_submit', view=edit_submit_view)
    app.add_template_searchpath(FOLDER)
    app.add_data_func(init_data)
    app.set_layout_template('notes_layout.jinja')

def init_data(app):
    engine = app.sqla_db_engine
    notes = db.Table('notes', metadata,
        db.Column('id', db.Integer, primary_key=True),
        db.Column('title', db.Unicode),
        db.Column('note', db.Unicode),
        db.Column('importance', db.Unicode)
    )
    db.mapper(Note, notes)
    metadata.create_all(engine)



if __name__ == '__main__':
    app = make_app(setup, FOLDER)
    run_very_simple(app)


