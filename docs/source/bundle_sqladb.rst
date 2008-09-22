
.. _bundle_sqladb:

SQLAlchemy Integration
======================

.. seealso::
   
   :ref:`external-references`

Glashammer comes ready with SQLAlchemy integration.

You can enable the support by adding the setup function for the bundle during
the application setup phase like so::

    from glashammer.bundles.sqladb import setup_sqladb

    app.add_setup(setup_sqladb)

The bundle will create a database engine and bind it to the configured URI.

The default URI can be passed in like so::

    app.add_setup(setup_sqladb, 'sqlite:////tmp/testdb.sqlite')

And this is then overridable by the configuration file.

Additionally a metadata instance is provided
:data:`glashammer.bundles.sqladb.metadata` which can be used to add ORM mapped objects
and tables.

The module also provides django-like database mappers, and these are explained
more fully in the API documentation below.

Getting the database engine
---------------------------

The database engine is stored on the application instance, and is thread-local
like the application. You can grab it at any time during data initialization
phase and request phase by using the :func:`get_engine` function:

.. autofunction:: glashammer.bundles.sqladb.get_engine


Creating database tables
------------------------

This is a semi-complete example of creating a full database table linked in to
the Glashammer database engine::

    from glashammer.bundles.sqladb import db, metadata, get_engine

    # Create the database table
    # (note that all SQLALchemy entities are copied in the db namespace)

    notes = db.Table('notes', metadata,
        db.Column('id', db.Integer, primary_key=True),
        db.Column('title', db.Unicode),
        db.Column('note', db.Unicode),
    )

    # Create the mapped ORM class
    class Note(object):
        """ Represents a note """
        def __init__(self, title, text, importance=None):
            self.title = title
            self.note = text

    # A special mapper that adds Django-like data managers
    db.mapper(Note, notes)

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

The generated db module
-----------------------

:data:`glashammer.bundles.sqladb.db` is a generated module which contains all the API
from the bundle as well as all the API that is imported from SQLAlchemy. This is
very useful as a quick shortcut.


Bundle cheat-sheet
------------------

Configuration variables
    * sqla_db_uri
        The sqlalchemy database URI (type: str, default:
        'sqlite:///<instance>/gh.sqlite')

Full API
--------

.. automodule:: glashammer.bundles.sqladb
    :members:
