# -*- coding: utf-8 -*-
# pylint: disable=abstract-method
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

import weechat_otr

class IsEncryptedContext(weechat_otr.IrcContext):

    def __init__(self, account, peername):
        super(IsEncryptedContext, self).__init__(account, peername)
        self.is_encrypted_fake = False

    def is_encrypted(self):
        return self.is_encrypted_fake
