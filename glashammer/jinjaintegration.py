

from jinja import ChoiceLoader, FileSystemLoader, Environment

from glashammer.utils import Service

def create_jinja_environment(paths):
    return Environment(loader=ChoiceLoader(
        [FileSystemLoader(path) for path in paths]
    ))


class JinjaService(Service):

    def lifecycle(self):
        self.directories = []

    def register(self, directory):
        self.directories.insert(0, directory)

    def finalise(self):
        self.env = self.jinja_environment = create_jinja_environment(
            self.directories)

