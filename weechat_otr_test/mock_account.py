# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

class MockAccount(object):

    def __init__(self):
        self.contexts = {}
        self.end_all_privates = 0

    def add_context(self, peer, context):
        self.contexts[peer] = context

    def getContext(self, peer):
        return self.contexts[peer]

    def end_all_private(self):
        self.end_all_privates += 1
