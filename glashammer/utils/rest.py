

"""
REST services for Glashammer
"""

class RestService(object):
    """
    Provides hooks for mounting REST on an endpoint.
    """

    def __call__(self, req, **kw):
        if req.method == 'GET':
            c = self.get
        elif req.method == 'POST':
            c = self.post
        elif req.method == 'PUT':
            c = self.put
        elif req.method == 'DELETE':
            c = self.delete
        else:
            c = None
        if c:
            return self.modifier(c(req, **req.args))
        else:
            return NotFound()

    def modifier(self, reponse):
        return response

    def post(self, req, **kw):
        return NotFound()

    def get(self, req, **kw):
        return NotFound()

    def put(self, req, **kw):
        return NotFound()

    def delete(self, req, **kw):
        return NotFound()


