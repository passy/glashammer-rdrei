

from glashammer.service import Service
from glashammer.plugins import Registry

class FeatureService(Service):

    def lifecycle(self):
        self.registry = Registry()

    def register(self, feature, provider):
        self.registry.register_feature(feature, provider)

    def list(self, feature):
        return self.registry.list_feature_providers(feature)
