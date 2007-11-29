
from glashammer.utils import Service

class ControllerService(Service):

    def lifecycle(self):
        self.controllers = {}

    def register(self, name, controller):
        self.controllers[name] = controller

    def get(self, name):
        return self.controllers.get(name)
