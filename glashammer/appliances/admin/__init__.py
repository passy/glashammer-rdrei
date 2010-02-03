
"""
glashammer.appliances.admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2010 Glashammer Developers
:license: MIT

The Glashammer Admin Appliance. This is mostly ported from the Pylons version
of FormAlchemy Admin application http://code.google.com/p/formalchemy/.
"""

from sqlalchemy import *
from sqlalchemy.orm import *

from werkzeug.exceptions import NotFound

from formalchemy import Grid, FieldSet
from formalchemy.templates import TemplateEngine
from formalchemy import config as formalchemy_config

from glashammer.utils.appliance import Appliance, expose
from glashammer.utils import render_response, redirect_to, render_template
from glashammer.bundles.sqlalchdb import setup_sqlalchdb, session, models,\
    ModelBase, get_engine


class FormalchemyJinja2TemplateEngine(object):

    def __init__(self, appliance, **kw):
        self.appliance = appliance
        self.template_kw = kw

    def _get_template_name(self, name):
        return '_admin/%s.jinja' % name

    def __call__(self, name, **kw):
        all_kw = self.template_kw.copy()
        all_kw.update(kw)
        return self.appliance.render_template(
            self._get_template_name(name), **all_kw)



class AdminUser(ModelBase):
    __tablename__ = 'adminusers'
    id = Column(Integer, primary_key=True)
    email = Column(Unicode)


class ModelsController(object):
    """Delegate the model based functionality"""
    def __init__(self):
        self.models = {}
        for model in models:
            self.models[model.__tablename__] = model
        print self.models

    def get_model_or_404(self, model_name):
        try:
            return self.models[model_name]
        except KeyError:
            raise NotFound()


class AdminAppliance(Appliance):
    """Glashammer Admin Appliance"""

    def __init__(self, **kw):
        Appliance.__init__(self, **kw)
        self.model = ModelsController()

    @expose('/')
    def index(self, req):
        return self.render_response('_admin/index.jinja', models=models,
        crumbs=['Home'])

    @expose('/<string:model_name>')
    def list(self, req, model_name):
        model = self.model.get_model_or_404(model_name)
        grid = Grid(model, model.query.all())
        grid.configure(readonly=True)
        grid.engine = self._create_fa_template_engine(model_name=model_name,
                                                      model_type=model)
        return self.render_response('_admin/list.jinja',
            model_name=model_name, grid=grid)

    @expose('/<string:model_name>/new')
    def new(self, req, model_name):
        model = self.model.get_model_or_404(model_name)
        if req.method == 'POST':
            item = model()
            fs = FieldSet(item, session=session, data=req.form)
            if fs.validate():
                fs.sync()
                item.save()
                session.commit()
                return self.redirect_to('list', model_name=model_name)
        else:
            fs = FieldSet(model, session=session)
        return self.render_response('_admin/new.jinja',
            item=None, model_name=model_name, fs=fs)

    @expose('/<string:model_name>/<int:id>/edit')
    def edit(self, req, model_name, id):
        model = self.model.get_model_or_404(model_name)
        item = model.query.get(id)
        if req.method == 'POST':
            fs = FieldSet(item, data=req.form)
            if fs.validate():
                fs.sync()
                item.save()
                session.commit()
                return self.redirect_to('list', model_name=model_name)
        else:
            fs = FieldSet(item)
        return self.render_response('_admin/new.jinja',
            item=item, model_name=model_name, fs=fs, crumbs=[model_name, 'Edit'])

    def setup_appliance(self, app):
        app.add_setup(setup_sqlalchdb)

    def _create_fa_template_engine(self, **kw):
        return FormalchemyJinja2TemplateEngine(self, **kw)


appliance = AdminAppliance

