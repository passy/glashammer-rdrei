
General Concepts
================

This chapter will discuss the general concepts involved in writing an
application with Glashammer. In principle, it would be very easy to just say
"Glashammer is MVC", but in practise this means very little.

Glashammer uses Werkzeug, which is a library of WSGI utilities. Most of the
actual components that will be used are straight from there, so a look at the
documentation at http://werkzeug.pocoo.org/documentation/ will certainly be worth
your while at some point.

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



