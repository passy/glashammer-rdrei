
import os, sys, pkgutil, cStringIO, string

import yaml

from jinja2 import Environment
from jinja2.loaders import BaseLoader
from jinja2.exceptions import TemplateNotFound

from sanescript import Command, Option, processors
from sanescript.config import Unset


class JinjaYamlLoader(BaseLoader):

    def __init__(self, data):
        stream = cStringIO.StringIO(data)
        stream.seek(0)
        self.templates = yaml.load(stream)

    def get_source(self, environment, name):
        try:
            return self.templates[name], name, lambda: False
        except KeyError:
            raise TemplateNotFound(name)


def _moduleify(name):
    accept = set(string.letters)
    return ''.join([c.lower() for c in name if c in accept])


class TemplateCommand(Command):

    template_data = None
    target = None

    exclude_interactive = ['template_file', 'target']

    base_options = [
        Option('target', help='The target in the template file to build.'),
        Option('output_directory', help='Output directory',
                default=os.path.abspath(os.getcwd()),
                processor=os.path.abspath),
    ]

    options = [] + base_options

    def _create_env(self, config):
        self.loader = JinjaYamlLoader(self.template_data)
        self.env = Environment(loader=self.loader)
        self.targets = self.loader.templates.get('__targets__')
        target_name = config.target or self.target
        if target_name is None:
            target_name = self.targets.keys()[0]
        self.target = self.targets.get(target_name)

    def __call__(self, config):
        if not config.package_name:
            config.grab_from_dict({'package_name':
                              _moduleify(config.project_name)})
        self._create_env(config)
        for k, v in self.target.items():
            self._visit_target(config, k, v, config.output_directory)

    def _visit_target(self, config, k, v, p):
        # the name could be a template
        name = self.env.from_string(k).render(config.to_dict())
        path = os.path.join(p, name)
        if isinstance(v, dict):
            os.mkdir(path)
            for k, v in v.items():
                self._visit_target(config, k, v, path)
        else:
            if isinstance(v, list):
                template_name, options = v
            else:
                template_name = v
                options = {}
            f = open(path, 'w')
            t = self.env.get_template(template_name)
            f.write(t.render(config.to_dict()))
            f.close()


class GHAdminTemplateCommand(TemplateCommand):

    template_data = pkgutil.get_data('glashammer', 'templates/ghadmin.yml')



