# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-instance-attributes

class MockContext(object):

    def __init__(self):
        self.smp_init = None
        self.smp_got_secret = None
        self.in_smp = False
        self.smp_finishes = []
        self.disconnects = 0
        self.encrypted = False
        self.verified = False
        self.logged = False

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

    def disconnect(self):
        self.disconnects += 1

    def is_encrypted(self):
        return self.encrypted

    def is_verified(self):
        return self.verified

    def is_logged(self):
        return self.logged
