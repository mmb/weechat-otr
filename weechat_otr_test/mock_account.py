class MockAccount(object):

    def __init__(self):
        self.contexts = {}

    def add_context(self, peer, context):
        self.contexts[peer] = context

    def getContext(self, peer):
        return self.contexts[peer]
