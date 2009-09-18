
"""
CouchDB support for Glashammer

This provides:

1. A thread local couch server instance for querying etc
2. A proxy to CouchDB
"""

from couchdb.client import Server, Resource

from werkzeug.exceptions import NotFound

from glashammer.utils import local, JsonResponse, Response


def create_server_event(server_url):
    def on_wsgi_call(server_url=server_url):
        local.couchdb_server = Server(server_url)
        local.couchdb_server_url = server_url
    return on_wsgi_call


def get_couchdb_server():
    """
    Retrieve the thread-local couchdb server instance.
    """
    return local.couchdb_server


def couch_proxy(req, path=''):
    r = Resource(None, local.couchdb_server_url)

    if req.method == 'GET':
        res = r.get(path, dict(req.headers), **req.args)

    elif req.method == 'DELETE':
        res = r.delete(path, dict(req.headers), **req.args)

    elif req.method == 'PUT':
        res = r.put(path, req.data, dict(req.headers), **req.args)

    elif req.method == 'POST':
        res = r.post(path, req.data, dict(req.headers), **req.args)

    return Response(res, mimetype="text/javascript")


def setup_couchdb(app, server_url='http://localhost:5984', mount_path='/couch'):
    """
    Add the couchdb bundle
    """

    app.add_config_var('couchdb/server_url', str, server_url)
    app.add_config_var('couchdb/mount_path', str, mount_path)

    mp = app.conf['couchdb/mount_path']
    su = app.conf['couchdb/server_url']

    app.connect_event('wsgi-call', create_server_event(su))

    app.add_url(mp + '/<path:path>', 'couchdb/proxy', view=couch_proxy)
    app.add_url(mp + '/', 'couchdb/proxy2', view=couch_proxy)


setup_app = setup_couchdb

