
from zope.interface import Interface

class ISiteConfig(Interface):

    def get_url_map():
        """
        Get the url map
        """
