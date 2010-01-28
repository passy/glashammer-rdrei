
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


def modelled(f):
    def _decorated(self, model_name, *args, **kw):
        print self
    return _decorated

class ModelsController(object):
    """Delegate the model based functionality"""
    def __init__(self):
        self.models = {}
        for model in models:
            self.models[model.__tablename__] = model

    def get_model_or_404(self, model):
        try:
            return self.models['model']
        except KeyError:
            raise NotFound()

class AdminAppliance(Appliance):
    """Glashammer Admin Appliance"""

    @expose('/')
    def index(self, req):
        return self.render_response('_admin/index.jinja')

    @modelled
    @expose('/<string:model>')
    def list(req, model):
        return self.render_response('_admin/index.jinja')

    @expose('/<string:model>/<int:id>')
    def view(req, model, id):
        pass

    def setup_appliance(self, app):
        app.add_setup(setup_sqlalchdb)


appliance = AdminAppliance

