# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

import weechat_otr_test.is_encrypted_context

import weechat_otr

class IsEncryptedAccount(weechat_otr.IrcOtrAccount):

    contextclass = weechat_otr_test.is_encrypted_context.IsEncryptedContext

    def __init__(self, name):
        super(IsEncryptedAccount, self).__init__(name)
