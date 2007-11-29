
import os

from glashammer.utils import Service, Controller

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'layout_templates')

NAVITEM = 'nav1-link'

from glashammer.ui import EndpointLink


class LayoutService(Service):

    def lifecycle(self):
        self.register_template_directory(TEMPLATE_PATH)
