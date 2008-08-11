
.. _databases:

Database Support
================

Support for databasing generally depends on the engine or ORM being used.
Glashammer doesn't try to push you in any one single direction, and so you are
free to choose whichever you like or even others.

.. toctree::
   :maxdepth: 1

   bundle_sqladb
   bundle_stormdb
   bundle_couchdb

The one frameworkish thing supplied by Glashammer is the ability to run a data
initialization callable during application setup. These are independent of setup
callables, because they are run at a time when it is ensured that all setup
functions have been completed.
