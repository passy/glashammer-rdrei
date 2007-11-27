

from jinja import ChoiceLoader, FileSystemLoader, Environment


def create_jinja_environment(paths):
    return Environment(loader=ChoiceLoader(
        [FileSystemLoader(path) for path in paths]
    ))

