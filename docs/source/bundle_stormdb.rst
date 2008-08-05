
.. _bundle_stormdb:

Storm Integration
=================

Glashammer supports the use of the Storm ORM.


Adding Storm support to your application
----------------------------------------

The support is added during application setup like so::

    from glashammer.bundles.stormdb import setup_stormdb
    app.add_setup(setup_stormdb)

An optional parameter can be passed which will be the default database URI,
which can then be overriden by the configuration file. This URI will be used if
the configuration file does not exist or does not contain the `storm/dburi`
configuration value::

    from glashammer.bundles.stormdb import setup_stormdb
    app.add_setup(setup_stormdb, 'sqlite:/home/ali/databases/helloworld.sqlite')


Accessing Stores
----------------

The :func:`glashammer.bundles.stormdb.get_store` function is provided that grabs
a correct store for your request or thread. This is a :class:`storm.store.Store`
instance and should be used as such. The only special thing about this store is
that it is a thread local instance, which it must be.

A simple example of such use::

    from glashammer.bundles.stormdb import get_store

    def index_view(req):
        store = get_store()
        return render_response('index.jinja', persons=store.find(Person))


Creating database tables
------------------------

You should read the Storm documentation which describes how to create ORM mapped
instances and tables.

.. seealso::

    * https://storm.canonical.com/Tutorial
    * https://storm.canonical.com/Manual
    * http://twistedmatrix.com/users/radix/storm-api/


Bundle cheat sheet
------------------

Configuration variables
    `storm/dburi`
        The URI of the database used by Storm.


Complete API
------------

.. automodule:: glashammer.bundles.stormdb
    :members:

