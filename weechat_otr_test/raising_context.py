# -*- coding: utf-8 -*-
# pylint: disable=abstract-method
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

import potr

import weechat_otr

class RaisingContext(weechat_otr.IrcContext):

    def __init__(self, account, peername):
        super(RaisingContext, self).__init__(account, peername)
        self.unencrypted = []

    def receiveMessage(self, messageData, appdata=None):
        if self.unencrypted:
            raise potr.context.UnencryptedMessage(*self.unencrypted)
        super(RaisingContext, self).receiveMessage(messageData, appdata)
