

from simplejson import dumps as dump_json, loads as load_json

from werkzeug import Response as wzResponse

class JSonResponse(wzResponse):
    default_mimetype = 'text/javascript'

    def __init__(self, data, *args, **kw):
        wzResponse.__init__(self, dump_json(data), *args, **kw)
