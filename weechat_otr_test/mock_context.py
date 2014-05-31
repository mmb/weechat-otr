# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

class MockContext(object):

    def __init__(self):
        self.smp_init = None
        self.smp_got_secret = None
        self.in_smp = False
        self.smp_finishes = []

    def smpAbort(self):
        pass

    def smpInit(self, *args):
        self.smp_init = args

    def smpGotSecret(self, *args):
        self.smp_got_secret = args

    def smp_finish(self, *args):
        self.smp_finishes.append(args)

    def print_buffer(self, *args):
        pass
