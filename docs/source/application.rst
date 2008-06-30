
The Glashammer Application
==========================

Almost the entire Glashammer API is available through the application instance
that will be passed to your setup callable. To create an application object,
call glashammer.make_app().

.. autofunction:: glashammer.application.make_app(setup_func, instance_dir)

which is linked to the endpoint
    >>> def my_setup(app):
    >>>     ...
    >>> from glashammer import make_app
    >>> app = make_app(my_setup, INSTANCE)

.. autoclass:: glashammer.application.GlashammerApplication
    :members: add_setup

.. automethod:: glashammer.application.GlashammerApplication.add_setup
