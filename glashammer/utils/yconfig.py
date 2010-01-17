

"""
glashammer.utils.yconfig
~~~~~~~~~~~~~~~~~~~~~~~~

Application declaration from yaml files.
<gulp>

For example::

    settings:
        db_uri: sqlite:///

    appliances:
        - import: glashammer.appliances.admin
          mountpoint_path: /admin
        - import: glashammer.appliances.pages
          mountpoint_path: /pages

    urls:
        - url: /blah/<int:id>
          endpoint: blah/view
          view: myapp.views.blah

    views:
        - endpoint: blah/view
          view: myapp.views.blah

    middlewares:
        - werkzeug.debugger.whatever

    config_vars:
        blah

    template_searchpaths:
        - /foo/blah
        - /moo/baz

    template_tags:
        - name: moo
          import: goo

    template_vars:
        - name: foo
          value: 12
        - name: foo
          import: foo.blah

    bundles:
        - glashammer.bundles.sqlalchdb.setup_sqlalchdb


"""

import os, sys

import yaml

from werkzeug import import_string
from flatland import Dict, String, List, String, Element
from flatland.validation.scalars import Present
from flatland import AdaptationError

from glashammer.utils import sibpath


class Import(String):

    def adapt(self, value):
        value = String.adapt(self, value)
        if value is not None:
            try:
                value = import_string(str(value))
            except ImportError, e:
                print 'Warning, failed to import %r' % value
                raise AdaptationError(str(e))
            return value

class Bundle(Import):

    def adapt(self, value):
        return Import.adapt(self,
            'glashammer.bundles.%s.setup_%s' % (value, value))

Url = Dict.of(
    String.named('url'),
    String.named('endpoint'),
    Import.named('view').using(optional=True),
)

Urls = List.of(Url)

Config = Dict.named('config').of(Dict)

Settings = Dict.of(Element)

TemplateSearchPaths = List.of(String)

TemplateFilter = Dict.of(
    Import.named('filter'),
    String.named('name'),
)

TemplateFilters = List.of(TemplateFilter)

SharedPath = Dict.of(
    String.named('name'),
    String.named('path'),
)

SharedPaths = List.of(SharedPath)

Appliance = Dict.of(
    Import.named('import'),
    String.named('mountpoint_path'),
)

Appliances = List.of(Appliance)

Setups = List.of(Import)

Bundles = List.of(Bundle)

def yconfig_setup(config_file, setup_func):

    f = open(config_file)
    config = yaml.load(f)
    f.close()

    sys.path.insert(0, os.path.dirname(config_file))

    def setup_app(app, config=config, setup_func=setup_func):

        # empty config file
        if config is None:
            return

        if setup_func is not None:
            app.add_setup(setup_func)

        # settings

        for bundle in Bundles(config.get('bundles')):
            if bundle.value is not None:
                app.add_setup(bundle.value)
            else:
                print 'bad bundle %r' % bundle.u
                # what to do if it is None?
                # Warning?

        # urls
        urls = Urls()
        urls.set(config.get('urls', []))

        if urls.validate():
            for url in urls.value:
                print url
                app.add_url(url['url'], url['endpoint'], url.get('view'))
        else:
            print 'failed'
            print [g.error for g in urls.all_children]



        for f in TemplateFilters(
            config.get('template_filters', [])
        ):
            if f['filter'] is not None:
                app.add_template_filter(f['name'].value, f['filter'].value)


        for searchpath in TemplateSearchPaths(
            config.get('template_searchpaths', [])
        ):
            sp = searchpath.value
            if not os.path.isabs(sp):
                sp = sibpath(config_file, sp)
            app.add_template_searchpath(sp)

        for sharedpath in SharedPaths(
            config.get('shared', [])
        ):
            p = sharedpath.value
            app.add_shared(p['name'], p['path'])


        for a in Appliances(
            config.get('appliances', [])
        ):
            appliance = a.value['import'](
                mountpoint_path=a.value['mountpoint_path'])
            app.add_setup(appliance)


    return setup_app






