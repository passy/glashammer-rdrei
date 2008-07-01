
General Concepts
================

This chapter will discuss the general concepts involved in writing an
application with Glashammer. In principle, it would be very easy to just say
"Glashammer is MVC", but in practise this means very little.

Glashammer uses Werkzeug, which is a library of WSGI utilities. Most of the
actual components that will be used are straight from there, so a look at the
documentation at http://werkzeug.pocoo.org/documentation/ ill certainly be worth
your while at some point.



Code Structure
--------------

On a file system, your Glashammer application occupies two distinct locations:

1. The location of the code for the application
2. The location of the instance of the application

In practise, these can be the same place, but it is important to be able to
differentiate them in order to run two instances of your application at the same
time.



