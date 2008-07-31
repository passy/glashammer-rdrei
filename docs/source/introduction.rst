.. _introduction:

Introduction
============

Glashammer Python web framework. Yes, yet another one.

Glashammer has lofty goals. Firstly something simple such as "hello
world" should be very simple, yet adding extra ready-components (such as an
admin interface) should also be very easy, and thus, batteries are very much
included.

Unlike a framework like Django, Glashammer is built using various proven
components. However, unlike a framework like Pylons, Glashammer decides what is
best for you in a number of situations. Choice is a great thing, and replacement
components are easy to add/replace, but the default configuration is complete.


Ready Components
----------------

The table below shows the various components used, and what they are used for:

+------------+--------------------------+
|  Library   | Use                      |
+============+==========================+
| Werkzeug   | WSGI utilities and more  |
+------------+--------------------------+
| Jinja2     | Templating               |
+------------+--------------------------+
| WTForms    | Form validation          |
+------------+--------------------------+

We have aimed to make some of these decisions for you by selecting these
components. You might hate one or more of them, in which case you could swap it out
easily enough, or just use a different framework like Pylons, which has a real
emphasis on making these things optional.


Application Phases
------------------

In general an application created with Glashammer has two phases:

1. Application Setup Phase
2. Request Phase


Application Setup Phase
~~~~~~~~~~~~~~~~~~~~~~~

This phase takes place during the constructor of the application instance.
During that time a number of callables can be registered which are run, which
extend the functionality of the application instance.

Once the constructor has completed, the configuration is "frozen" and the
functionality is preserved in order to serve requests during the Request Phase.

The details of the Application setup phase are found in :ref:`application`.


Request Phase
~~~~~~~~~~~~~

The request phase takes place during the actuall HTTP request made to the web
application. During this phase the application handles the request in the ways
that the application setup phase has outlined.


Code Structure
--------------

On a file system, your Glashammer application occupies two distinct locations:

1. The location of the code for the application
2. The location of the instance of the application

In practise, these can be the same place, but it is important to be able to
differentiate them in order to run two instances of your application at the same
time.


Bundles
-------

Bundles are pluggable application components. The can to anything to your
application (such as add urls and views, or very little such as add a
template global variable).

Bundles are initialised just by importing and calling the setup_app function
from the bundle's module. That is the only requirement for a bundle, a
callable that takes an application instance.

We provide a number of bundles, but encourage you to use them as very
lightweight reusable components between your web applications.

