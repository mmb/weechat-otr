class MockContext(object):

    def __init__(self):
        self.smp_init = None

    def smpInit(self, *args):
        self.smp_init = args

    def print_buffer(self, *args):
        pass
