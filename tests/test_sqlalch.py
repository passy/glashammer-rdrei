# -*- coding: utf-8 -*-
"""
tests.test_sqlalch
~~~~~~~~~~~~~~~~~~

Tests for the sqlalchemy bundle.

:copyright: 2009-2010, The Glashammer Authors
:license: MIT
"""


from __future__ import with_statement
import os
from os import path

from sqlalchemy import Table, Column, types, UniqueConstraint
from sqlalchemy.orm import mapper
from sqlalchemy.exc import IntegrityError
from simplejson import loads
from werkzeug.test import Client
from glashammer.application import make_app
from glashammer.utils import get_app, get_request
from glashammer.utils.wrappers import Response
from glashammer.bundles.sqlalchdb import metadata, setup_sqlalchdb, session, \
        refresh_engine, ModelBase, data_init, get_engine
from nose.tools import assert_raises


class TestSQLA(object):

    def setup(self):
        if os.path.exists(path.join('test_output', 'gh.sqlite')):
            os.unlink(path.join('test_output', 'gh.sqlite'))


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

        def setup_app(app):
            app.add_setup(setup_sqlalchdb, 'sqlite://')

        self._setup_app = setup_app

        refresh_engine()
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


class Author(ModelBase):
    """Model representing an author."""
    __tablename__ = 'author'
    __table_args__ = (UniqueConstraint(
        'first_name', 'last_name'
    ), {})

    id = Column(types.Integer, primary_key=True, autoincrement=True)
    first_name = Column(types.String(60))
    last_name = Column(types.String(60))


SQLA_TRACK_CONFIG = """
[database]
track_queries = True
"""

class TestSQLADeclarative(object):

    def setup_app(self, app):
        app.add_setup(setup_sqlalchdb, 'sqlite:///')
        app.add_url('/', '', view=self._query_view)

    def setup(self):
        """Creates a test environment."""

        if os.path.exists(path.join('test_output', 'gh.sqlite')):
            os.unlink(path.join('test_output', 'gh.sqlite'));

        with open(path.join('test_output', 'config.ini'), 'w') as file:
            file.write(SQLA_TRACK_CONFIG)

        refresh_engine()
        self.app = make_app(self.setup_app, 'test_output')
        data_init()
        # Bind the model to the new engine

        Author.metadata.bind = get_engine()

    def teardown(self):
        """Removes database and config"""

        try:
            os.unlink(path.join('test_output', 'gh.sqlite'))
            os.unlink(path.join('test_output', 'config.ini'))
        except OSError:
            pass

    def test_engine(self):
        assert self.app.sqla_db_engine is get_app().sqla_db_engine

    def test_model(self):
        """Creates some new objects in the database and tries to query
        them.

        """

        # Creates some authors
        author1 = Author()
        author1.first_name = "Pascal"
        author1.last_name = "Hartig"

        author2 = Author()
        author2.first_name = "Ali"
        author2.last_name = "Afshar"

        session.add_all([author1, author2])
        session.commit()

        # Catch unique constraint failures
        author3 = Author()
        author3.first_name = "Pascal"
        author3.last_name = "Hartig"
        session.add(author3)

        assert_raises(IntegrityError, lambda: session.commit())
        session.rollback()

        self._test_author_queries()

    def _test_author_queries(self):
        """Tries to query the previously creates authors."""

        query = session.query(Author)

        result = query.filter_by(first_name="Pascal").one()

        assert result.first_name == "Pascal"
        assert result.last_name == "Hartig"

        result = query.get(2)

        assert result.first_name == "Ali"
        assert result.last_name == "Afshar"

    def _query_view(self, request):
        """Doing a single query."""

        query = session.query(Author)

        result1 = query.filter(Author.first_name.like("Pas%")).count()
        result2 = query.all()

        return Response(str(result1))

    def test_query_tracking(self):
        """Tests query tracking."""

        client = Client(self.app, Response)

        response = client.get('/')
        request = get_request()

        assert len(request.sql_queries) == 2
        assert response.headers['X-SQL-Query-Count'] == '2'
        assert response.headers['X-SQL-Query-Time'] > 0
