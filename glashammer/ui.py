


class EndpointLink(object):

    def __init__(self, label, endpoint, argdict={}):
        self.endpoint = endpoint
        self.argdict = argdict
        self.label = label

    def get_url(self, map_adapter):
        return map_adapter.build(self.endpoint, self.argdict)
