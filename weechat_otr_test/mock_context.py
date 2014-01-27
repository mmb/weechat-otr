# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

class MockContext(object):

    def __init__(self):
        self.smp_init = None
        self.smp_got_secret = None

    def smpInit(self, *args):
        self.smp_init = args

    def smpGotSecret(self, *args):
        self.smp_got_secret = args

    def print_buffer(self, *args):
        pass
