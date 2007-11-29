# -*- coding: utf-8 -*-
#
# Copyright 2007 Glashammer Project
#
# The MIT License
#
# Copyright (c) <year> <copyright holders>
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
