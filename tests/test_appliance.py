
from glashammer.utils.appliance import Appliance, expose

from tests import gh_app


class Pages(Appliance):

    @expose('/')
    def view_index(self):
        pass

def _setup(app):
    p = Pages()
    app.add_setup(p)

def test_appliance():
    gh_app(_setup)


