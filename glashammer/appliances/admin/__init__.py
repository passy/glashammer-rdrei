
"""
glashammer.appliances.admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2010 Glashammer Developers
:license: MIT

The Glashammer Admin Appliance. This is mostly ported from the Pylons version
of FormAlchemy Admin application http://code.google.com/p/formalchemy/.
"""

from glashammer.utils.appliance import Appliance, expose
from glashammer.utils import render_response, redirect_to

from glashammer.bundles.sqlalchdb import setup_sqlalchdb, session, models

class AdminAppliance(Appliance):
    """Glashammer Admin Appliance"""

    @expose('/')
    def index(self, req):
        return self.render_response('_admin/index.jinja')

    @expose('/<string:model>')
    def list(req, model):
        pass

    @expose('/<string:model>/<int:id>')
    def view(req, model, id):
        pass

    def setup_appliance(self, app):
        app.add_setup(setup_sqlalchdb)


appliance = AdminAppliance

