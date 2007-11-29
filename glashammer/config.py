


from glashammer.service import Service

class MissingRequiredConfigOption(KeyError):
    """Raised when a required config option is missing"""


class ConfigOption(object):

    def __init__(self, name, default):
        self.name = name
        self.default = default


class ConfigService(Service):

    def lifecycle(self):
        self.options = {}

    def register(self, name, default=None):
        opt = ConfigOption(name, default)
        self.options[name] = opt

    def finalise(self):
        self.config = self.get_config()

    def get(self, name):
        return self.config.get(name)

    def get_default_config(self):
        conf = {}
        for k, v in self.options.items():
            if v.default is not None:
                conf[k] = v.default
        return conf

    def check_config(self, conf):
        for k in self.options:
            if k not in conf:
                raise MissingRequiredConfigOption(k)

    def get_config(self):
        conf = self.get_default_config()
        conf.update(self.site.site_config)
        self.check_config(conf)
        return conf


