
.. _config:

Configuration Variables
=======================

Your Glashammer application has automatic configuration built in. It doesn't
actually need a configuration file, and if Glashammer doesn't find one, the
default values are  used.

Glashammer will search for a config file called "config.ini" in the instance
directory of your application. If this file is found Glashammer will use it to
override the default settings. This file is a human-writable/readable
ini-style file which is designed to be able to be edited by hand if required.

Configuration variables can generally be one of the python types:

    * `str`
    * `int`
    * `bool`


Adding a configuration value
----------------------------

During the application setup phase, config variables can be added using:

.. automethod:: glashammer.application.GlashammerApplication.add_config_var

So for example a simple configuration variable for whether the application is
in maintenance mode might be added like::

    app.add_config_var('maintenance_mode', bool, False)


Reading configuration variables
-------------------------------

A configuration variable can be read after application setup durin the request
phase by using the app.conf as a dict-like item.

For example::

    if app.conf['maintenance_mode']:
        # the application is in maintenance mode
        return redirect('/maintenance')


Setting a configuration variable
--------------------------------

You can set configuration variables using the set method of the configuration
object:

.. automethod:: glashammer.utils.Configuration.change_single

This method ensures that the value is changed and written in a transaction to
avoid concurrency issues. So to continue our example, to set the
'maintenance_mode' variable::

    app.conf.change_single('maintenance_mode', True)


Other backends
--------------

Currently only a file-based configuration backend exists, but this can be
non-ideal in some situations. For example, when using Google AppEngine, the
configuration file will have to be created offline and uploaded, and the
configuration will not be able to be changed from the running app.

For these kinds of reasons, we encourage developers to come up with
alternative backends which solve these kinds of problems. The interface is
relatively simple, so the task should be simple.


