

from simplejson import dumps as dump_json, loads as load_json

from werkzeug import Response as wzResponse
from werkzeug.exceptions import NotFound

class JsonResponse(wzResponse):
    default_mimetype = 'text/javascript'

    def __init__(self, data, *args, **kw):
        wzResponse.__init__(self, dump_json(data), *args, **kw)


class JsonRestService(object):

    def __call__(self, req, **kw):
        if req.method == 'GET':
            return self.get(req, **kw)
        elif req.method == 'POST':
            return self.post(req, **kw)
        elif req.method == 'PUT':
            return self.put(req, **kw)
        elif req.method == 'DELETE':
            return self.delete(req, **kw)
        else:
            return NotFound()

    def post(self, req, **kw):
        return NotFound()

    def get(self, req, **kw):
        return NotFound()

    def put(self, req, **kw):
        return NotFound()

    def delete(self, req, **kw):
        return NotFound()


def json_view(f):
    """
    Decorator to jsonify responses
    """
    def _wrapped(*args, **kw):
        res = f(*args, **kw)
        if callable(res):
            return res
        else:
            return JsonResponse(res)
    return _wrapped
