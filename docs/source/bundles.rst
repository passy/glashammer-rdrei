
Bundles
=======

Bundles are reusable components that can be easily swapped between
applications. The only requirement for a bundle is that it has a callable that
accepts the application instance. This setup function is much like the setup
function passed to an application on initial setup. The bundle's setup
function is called during application setup and the functionality.

.. automethod:: glashammer.application.GlashammerApplication.add_setup
