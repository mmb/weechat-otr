# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

import potr

import weechat_otr

class RaisingContext(weechat_otr.IrcContext):

    def __init__(self, account, peername):
        super(RaisingContext, self).__init__(account, peername)
        self.unencrypted = None

    def receiveMessage(self, *args):
        if self.unencrypted:
            raise potr.context.UnencryptedMessage(*self.unencrypted)
        super(RaisingContext, self).receiveMessage(*args)
