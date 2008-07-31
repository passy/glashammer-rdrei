
.. _gh-admin:

gh-admin utility
================

Glashammer installs a script used for doing useful Glashammer-related things. In
fact, it will probably end up as a jumble of lots of useful things in one place,
but for now there are a number of functions.

The gh-admin script will be installed in your path on installation of
Glashammer, or it can be found in the bin/ directory if using directly from the
source.

The basic syntax is this::

    gh-admin <action> [args]

Where an action is a single task. The actions available ar eoutlines below.

Running Glashammer applications
-------------------------------

Glashammer applications (or Python scripts that create them) can be run for
debugging directly by filename using the `run` action::

    gh-admin run <modulepath>

For example::

    $ gh-admin run examples/helloworld/run.py

The only requirement in this case is that the run module have a callable
`create_app` which will return a WSGI application when called with no arguments.

An example `create_app` method might go like this::

    from glashammer import make_app

    def my_app_setup(app):
        """Set up the application"""

    def create_app():
        return make_app(my_app_setup)

The actual name of the callable called to create the application can be modified
by passing the `--application-factory-name` option (which is set to "create_app"
by default).

The complete list of options for the run command are listed in the usage
information::

    Run a WSGI Debug server with an application

    gh-admin runserver <modulepath> [application_factory_name] [options]

    Modulepath is the path to a Python module which contains the callable
    named in the application_factory_name variable. This callable is called
    and expects to receive a WSGI application (eg a GlashammerApplication)
    instance.

    --modulepath                  string
    --application-factory-name    string    create_app
    -h, --hostname                string    localhost
    -p, --port                    integer   6060
    --no-reloader
    --no-debugger
    --no-evalex
    --threaded
    --processes                   integer   1


Checking Glashammer dependencies are installed
----------------------------------------------

Glashammer can give you a status report on the required modules it needs to run.
This is achieved using the `dependencies` action::

    $ gh-admin dependencies
    Werkzeug...		Installed
    Jinja2...		Installed
    WTForms...		Installed


Checking Glashammer is the latest available version
---------------------------------------------------

If you have an internet connection, you can check whether Glashammer is the
latest available version in PyPi by using the `checkversion` action::

    gh-admin checkversion

Optionally passing the `--upgrade` option to checkversion will tell the script
to attempt to upgrade Glashammer using `easy_install`.

.. note:: You may need super-user capabilities to upgrade.


.. gh-admin_staticaliases

Generating a static file Alias map
----------------------------------

Static files served through WSGI are generally slow, process-intensive and lacks
a load of web-server features that "real" web servers take for granted. For
this reason we like to serve them with a real web server.

.. seealso::

    :ref:`statics`

The `staticaliases` action reads the application and generates the map. This can then
be placed in your web server configuration file, for example with an example
Glashammer application::

    $ gh-admin staticaliases examples/jsonrest/run.py
    Alias /_shared/glashammer /home/ali/working/glashammer-main/glashammer/shared



Showing the Glashammer version
------------------------------

This doesn't need much introduction::

    gh-admin version


