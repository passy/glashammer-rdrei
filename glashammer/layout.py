
import os

from glashammer.utils import Service

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'layout_templates')

class LayoutService(Service):

    def lifecycle(self):
        self.register_template_directory(TEMPLATE_PATH)
