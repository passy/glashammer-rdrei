
import os

from sqlalchemy import Table, Column, types
from sqlalchemy.orm import mapper

from simplejson import loads

from werkzeug.test import Client

from glashammer.application import make_app
from glashammer.utils import get_app
from glashammer.bundles.sqlalchdb import metadata, setup_sqlalchdb, session


class TestSQLA(object):

    def setup(self):
        if os.path.exists('test_output/gh.sqlite'):
            os.unlink('test_output/gh.sqlite')


        if metadata.bind:
            metadata.drop_all()


        # The SQLA tables
        notes = Table('notes', metadata,
            Column('id', types.Integer, primary_key=True),
            Column('title', types.Text),
            Column('note', types.Text),
            Column('importance', types.Text),
            useexisting=True,
        )

        # The ORM mapped class
        class Note(object):
            """ Represents a note """

        self.Note = Note

        # Make a mapper which gives you the objects manager
        mapper(Note, notes)


        def setup_db(app):
            notes.create(app.sqla_db_engine)

        def setup_app(app):
            app.add_setup(setup_sqlalchdb)
            app.add_data_func(setup_db)

        self.app = make_app(setup_app, 'test_output')
        self.c = Client(self.app)

    def test_engine(self):
        assert get_app().sqla_db_engine

    def test_objects(self):
        assert session.query(self.Note).count() == 0
        for t in 'abcdef':
            n = self.Note()
            n.title = n.note = n.importance = t
            session.add(n)
        session.commit()
        assert session.query(self.Note).count() == 6

