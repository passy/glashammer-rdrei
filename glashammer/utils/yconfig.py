

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


"""

import yaml

from werkzeug import import_string
from flatland import Dict, String, List, String, Element
from flatland.validation.scalars import Present
from flatland import AdaptationError


class Import(String):

    def adapt(self, value):
        value = String.adapt(self, value)
        if value is not None:
            try:
                value = import_string(value)
            except ImportError, e:
                raise AdaptationError(str(e))
            return value


Url = Dict.of(
    String.named('url'),
    String.named('endpoint'),
    Import.named('view').using(optional=True),
)

Urls = List.of(Url)

Config = Dict.named('config').of(Dict)

Settings = Dict.of(Element)

TemplateSearchPaths = List.of(String)

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

def yconfig_setup(config_file, setup_func):

    f = open(config_file)
    config = yaml.load(f)
    f.close()

    def setup_app(app, config=config, setup_func=setup_func):

        # empty config file
        if config is None:
            return

        if setup_func is not None:
            app.add_setup(setup_func)

        # settings

        # urls
        urls = Urls()
        urls.set(config.get('urls', []))

        if urls.validate():
            for url in urls.value:
                app.add_url(url['url'], url['endpoint'], url.get('view'))
        else:
            print 'failed'
            print [g.error for g in urls.all_children]


        for searchpath in TemplateSearchPaths(
            config.get('template_searchpaths', [])
        ):
            app.add_template_searchpath(searchpath.value)

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






