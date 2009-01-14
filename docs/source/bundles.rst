
.. _bundles:

Bundles
=======

Bundles are reusable components that can be easily swapped between
applications. The only requirement for a bundle is that it has a callable that
accepts the application instance. This setup function is much like the setup
function passed to an application on initial setup. The bundle's setup
function is called during application setup and the functionality.

.. automethod:: glashammer.application.GlashammerApplication.add_setup

The following bundles are shipped with Glashammer, expect this list to increase,
as we are adding functionality as required.

.. toctree::
    :maxdepth: 1

    bundle_forms
    bundle_sessions
    bundle_repozewho
    bundle_auth
    bundle_i18n
    bundle_sqladb
    bundle_stormdb
    bundle_htmlhelpers
    bundle_gae

.. note::

   If you have a bundle you have written, and reuse, the chances are that others
   will find it useful too, so please tell us about it for inclusion into the
   source.

