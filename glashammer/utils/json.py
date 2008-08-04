# -*- coding: utf-8 -*-
"""
    glashammer.utils.json
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2007-2008 by Ali Afshar
    :license: MIT
"""

from simplejson import dumps as dump_json, loads as load_json

from werkzeug import Response as wzResponse
from werkzeug.exceptions import NotFound

from glashammer.utils.rest import RestService


class JsonResponse(wzResponse):
    default_mimetype = 'text/javascript'

    def __init__(self, data, *args, **kw):
        wzResponse.__init__(self, dump_json(data), *args, **kw)


class JsonRestService(RestService):

    def modifier(self, response):
        if callable(response):
            return response
        else:
            return JsonResponse(response)


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

