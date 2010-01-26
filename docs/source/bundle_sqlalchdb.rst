
.. _bundle_sqlalchdb:

SQLAlchemy Integration
======================

.. seealso::

   :ref:`external-references`

Glashammer comes ready with SQLAlchemy integration.

You can enable the support by adding the setup function for the bundle during
the application setup phase like so::

    from glashammer.bundles.sqlalchdb import setup_sqlalchdb

    app.add_setup(setup_sqlalchdb)

The bundle will create a database engine and bind it to the configured URI.

The default URI can be passed in like so::

    app.add_setup(setup_sqlalchdb, 'sqlite:////tmp/testdb.sqlite')

And this is then overridable by the configuration file.

Additionally a metadata instance is provided
:data:`glashammer.bundles.sqlalchdb.metadata` which can be used to add ORM mapped objects
and tables.

The module also provides django-like database mappers, and these are explained
more fully in the API documentation below.

Using declarative database definitions
--------------------------------------

The SQLAlch bundle provides ready base-classes to use as declarative table
definitions which are described in the SQLAlchemy documentation:
http://www.sqlalchemy.org/docs/reference/ext/declarative.html.

The base model class provided is available at
`glashammer.bundles.sqlalchdb.ModelBase` and can be used as::

    from sqlalchemy import Column, Integer, Unicode

    from glashammer.bundles.sqlalchdb import ModelBase

    class Customer(ModelBase):
        __tablename__ = 'customers'
        id = Column(Integer, primary_key=True)
        name = Column(Unicode)

This class can then be used as any mapped SQLAlchemy class, although it has
some additional properties which are described later in this document.


.. Note::
    The only difference between glashammer's declarative use, and vanilla
    SQLAlchemy use is that the Base model has already been created for
    you, and bound correctly to the correct metadata instance, and has been
    extended to provide some methods that are session bound (in the
    thread-local context). If you wish to know how it does this, please review
    the source code, it is all standard SQLAlchemy API usage.


Getting the database session
----------------------------

Glashammer's database session is a sqlalchemy ScopedSession, so it can be used
as a module-level global, but can be assured to be thread-local. It is
automatically cleaned up at the end of each request.

To retrieve the session, use it as so::

    from glashammer.bundles.sqlalchdb import session
    session.query(Bird).filter_by(name='goose')


Getting the database engine
---------------------------

The database engine is stored on the application instance, and is thread-local
like the application. You can grab it at any time during data initialization
phase and request phase by using the :func:`get_engine` function:

.. autofunction:: glashammer.bundles.sqlalchdb.get_engine


Creating database tables
------------------------

This is a semi-complete example of creating a full database table linked in to
the Glashammer database engine::

    from glashammer.bundles.sqlalchdb import metadata, get_engine

    from sqlalchemy import Table, Column, Unicode
    from sqlalchemy.orm import mapper

    # Create the database table
    notes = Table('notes', metadata,
        Column('id', Integer, primary_key=True),
        Column('title', Unicode),
        Column('note', Unicode),
    )

    # Create the mapped ORM class
    class Note(object):
        """ Represents a note """
        def __init__(self, title, text, importance=None):
            self.title = title
            self.note = text

    # A special mapper that adds Django-like data managers
    mapper(Note, notes)

    # A callable to initialize the database
    def setup_data(app):
        metadata.create_all(get_engine())

    # The application setup callable
    def setup(app):
        app.add_data_func(setup_data)

    # Now create your application, and run it how you like
    app = make_app(setup, '/my/instance/directory')

This code is modified from the examples/notes application, to which you may
refer for more examples.

Database initialization
-----------------------

Any callable to do some database initialization, such as creating tables, should
be added to the application during setup phase using app.add_data_func

.. automethod:: glashammer.application.GlashammerApplication.add_data_func

This is separate from the setup callables in that they are run afterwards, so we
can be sure that code requiring this bundle's initialization has been called.


Bundle cheat-sheet
------------------

Configuration variables
    * db.uri
        The sqlalchemy database URI (type: str, default:
        'sqlite:///<instance>/gh.sqlite')

Full API
--------

.. automodule:: glashammer.bundles.sqlalchdb
    :members:
