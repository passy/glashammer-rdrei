
import os

from glashammer.bundle import Bundle
from glashammer.controller import Controller

package_dir = os.path.dirname(__file__)

TEMPLATE_PATH = os.path.join(package_dir, 'layout_templates')
STATIC_PATH = os.path.join(package_dir, 'layout_public')

NAVITEM = 'nav1-link'

from glashammer.ui import EndpointLink


class LayoutBundle(Bundle):

    def lifecycle(self):
        self.register_template_directory(TEMPLATE_PATH)
        self.register_static_directory('/layout', STATIC_PATH)
