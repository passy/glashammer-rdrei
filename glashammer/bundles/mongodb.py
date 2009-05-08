# -*- coding: utf-8 -*-

# Copyright (c) 2009 Glashammer Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""MongoDB integration for Glashammer.

MongoDB is a document-oriented data store that is easy to deploy, manage
and use. Any important features are:

   - High performance
   - Full index support
   - Query profiling
   - Replication and fail-over support
   - Efficient storage of binary data including large objects
   - Auto-sharding for cloud-level scalability

   http://www.mongodb.org/display/DOCS/Home

* Installation:
   http://www.mongodb.org/display/DOCS/Getting+Started
   http://www.mongodb.org/display/DOCS/Python+Language+Center

* Tutorial:
   http://www.mongodb.org/display/DOCS/Python+Tutorial

* Python driver API:
   http://api.mongodb.org/python/

"""
__author__ = 'Jonás Melián <devel@jonasmelian.com>'
__copyright__ = '(c) 2009 Glashammer Developers'
__license__ = 'MIT X11'
__date__ = '2009-05-08'  # yyyy-mm-dd


try:
   from pymongo import connection
except ImportError, err:
   raise ImportError("%s\nRead about its installation in the docstring." % err)


def setup_mongodb(app, host=None, port=None, pool_size=None,
                  auto_start_request=None):
   """Adds the Mongo DB bundle.

   The connector constructor parameters are by default:

   host='localhost', port=27017, pool_size=1, auto_start_request=True

   as you can see in its API:

   http://api.mongodb.org/python/0.9.5/pymongo.connection.Connection-class.html

   """
   app.add_config_var('mongodb/host', str, host)
   app.add_config_var('mongodb/port', int, port)
   app.add_config_var('mongodb/pool_size', int, pool_size)
   app.add_config_var('mongodb/auto_start_request', bool, auto_start_request)

   def _open_connection():
      """Opens a new connection to a Mongo instance at host:port."""
      host = app.conf['mongodb/host']
      port = app.conf['mongodb/port']
      pool_size = app.conf['mongodb/pool_size']
      auto_start_request = app.conf['mongodb/auto_start_request']

      try:
         db_connection = connection.Connection(
               host=host, port=port, pool_size=pool_size,
               auto_start_request=auto_start_request)
      except connection.ConnectionFailure:
         # Gets the values that are used to connect to Mongo server.
         if not host:
            _host = connection.Connection.HOST
         else:
            _host = host
         if not port:
            _port = connection.Connection.PORT
         else:
            _port = port

         print("Could not connect. Be sure that Mongo is running on %s:%d" %
               (_host, _port))

      # 'local' is 1 per thread, 'app' might be shared between thread.
      # So if the connection object is thread safe (Pymongo does),
      # you can use 'app', otherwise you will need a connection per thread.
      #
      # local.mongodb_connection = db_connection
      app.mongodb_connection = db_connection

   app.connect_event('wsgi-call', _open_connection)


setup_app = setup_mongodb
