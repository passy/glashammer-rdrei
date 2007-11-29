
"""
Basic Plugin support

>>> class IBanana(object):
...     '''A Fake Interface'''

>>> class Banana(object):
...     '''Something that does something'''

>>> b = Banana()

>>> r = Registry()
>>> r.register_singleton(IBanana, b)
>>> b2 = r.get_singleton(IBanana)
>>> b is b2
True

>>> b3 = Banana()
>>> b4 = Banana()

>>> r = Registry()
>>> r.register_feature(IBanana, b3)
>>> r.register_feature(IBanana, b4)

>>> feats = r.get_feature_providers(IBanana)
>>> b3 in feats
True
>>> b4 in feats
True
>>> len(feats)
2
"""

class SingletonRegisteredError(ValueError):
    """
    Singleton is already registered.
    """

class PluginLookupError(KeyError):
    """
    Plugin does not exist.
    """

class Registry(object):
    """
    A registry provides a place to store details about plugins, of which there
    are two types, singletons, and features.


    """

    def __init__(self):
        self._singletons = {}
        self._features = {}

    def register_singleton(self, token, plugin):
        if token in self._singletons:
            raise SingletonRegisteredError('Singleton exists for %r' % token)
        else:
            self._singletons[token] = plugin

    def register_feature(self, token, plugin):
        self._features.setdefault(token, []).append(plugin)

    def get_singleton(self, token):
        try:
            return self._singletons[token]
        except KeyError:
            raise PluginLookupError('No plugin exists for %r' % token)

    def list_feature_providers(self, token):
        try:
            return list(self._features[token])
        except KeyError:
            return []

        
def _test():
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)

if __name__ == "__main__":
    _test()
