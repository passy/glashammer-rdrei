
General Concepts
================

This chapter will discuss the general concepts involved in writing an
application with Glashammer. In principle, it would be very easy to just say
"Glashammer is MVC", but in practise this means very little.

Glashammer uses Werkzeug, which is a library of WSGI utilities. Most of the
actual components that will be used are straight from there, so a look at the
documentation at http://werkzeug.pocoo.org/documentation/ ill certainly be worth
your while at some point.


Creating an application instance
--------------------------------

Application instances should be created using glashammer.make_app:

.. autofunction:: glashammer.make_app

The passed setup_func is a callable that will be the main entry point into the
application. It is in this function that the application is configured.
Throughout this manual when we refer to a "setup function" this is what we are
referring to.

The instance directory is where the data for one particular instance of an
applicaiton lives. This is explained in more detail in the next section.


Code Structure
--------------

On a file system, your Glashammer application occupies two distinct locations:

1. The location of the code for the application
2. The location of the instance of the application

In practise, these can be the same place, but it is important to be able to
differentiate them in order to run two instances of your application at the same
time.



