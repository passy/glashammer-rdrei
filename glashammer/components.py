
try:
    from zope.interface import Interface
except ImportError:
    class Interface(object):
        """A dummy interface object"""
