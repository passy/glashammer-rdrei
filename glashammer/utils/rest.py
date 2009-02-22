from werkzeug.exceptions import MethodNotAllowed

"""
REST services for Glashammer
"""

class RestService(object):
    """
    Provides hooks for mounting REST on an endpoint.
    """
    #XXX: implement a sane default for options
    possible_methods = 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'

    def __call__(self, req, **kw):
        handler = self._get_handler(req)
        if handler:
            response = handler(req, **kw)
            return self.modifier(response)
        else:
            return MethodNotAllowed(valid_methods=self._get_methods())

    @staticmethod
    def _nice_name(method):
        return method.lower().replace('-','_')

    def _get_methods(self):
        methods = []
        for method in self.possible_methods:
            if getattr(self, self._nice_name(method), None) is not None:
                options.append(method)
        return methods

    def _get_handler(self, req):
        if req.method not in self.possible_methods:
            return
        nice_name = self._nice_name(req.method)
        return getattr(self, nice_name, None)

    def modifier(self, reponse):
        return response

