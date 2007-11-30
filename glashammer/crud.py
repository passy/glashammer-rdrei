
from formencode import Schema, Invalid

from glashammer.controller import Controller
from werkzeug.routing import Rule


class CrudController(Controller):

    """
    A basic crud controller
    """

    base_url = None
    index_template = None
    view_template = None
    form_template = None
    model_type = None
    schema_type = None

    def index(self, req):
        return self.create_template_response(req, self.index_template,
                items=self.site.storm.store.find(self.model_type))

    def view(self, req, id):
        item = self.site.storm.store.find(self.model_type, id=id).one()
        if item is None:
            return NotFoundResponse()
        else:
            return self.create_template_response(req, self.view_template,
                                             item=item)

    def edit(self, req, id):
        item = self._get_item_for_id(id)
        if item is None:
            return NotFoundResponse()
        else:
            return self.create_template_response(req, self.form_template,
                                            item=item)

    def new(self, req):
        item = self.model_type()
        return self.create_template_response(req, self.form_template,
                                             item=item)

    def save(self, req):
        try:
            values = self._validate_form(req)
            store = self.site.storm.store
            id = values.get('id')
            del values['id']
            if id:
                item = self._get_item_for_id(id)
                for k in values:
                    setattr(item, k, values[k])
            else:
                item = self.model_type()
                for k in values:
                    print item, k, values[k]
                    setattr(item, k, values[k])
                store.add(item)
            #store.flush()
            store.commit()
            return RedirectResponse(self.base_url + '/%s' % item.id)
        except Invalid, e:
            item = None
            print e.unpack_errors()
            return self.create_template_response(req, self.form_template,
                        item=item, prefill=req.form, errors=e.unpack_errors())

    def _validate_form(self, req):
        schema = self.schema_type()
        values = schema.to_python(req.form)
        return values

    def _get_item_for_id(self, id):
        item = self.site.storm.store.find(self.model_type, id=id).one()
        return item

    @classmethod
    def generate_urls(cls):
        return [
            Rule(cls.base_url,
                endpoint='%s/index' % cls.endpoint_name),
            Rule(cls.base_url + '/<int:id>',
                endpoint='%s/view' % cls.endpoint_name),
            Rule(cls.base_url + '/<int:id>/edit',
                endpoint='%s/edit' % cls.endpoint_name),
            Rule(cls.base_url + '/save',
                endpoint='%s/save' % cls.endpoint_name),
            Rule(cls.base_url + '/new',
                endpoint='%s/new' % cls.endpoint_name),
        ]

