# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

import weechat_otr_test.raising_context

import weechat_otr

class RaisingAccount(weechat_otr.IrcOtrAccount):

    contextclass = weechat_otr_test.raising_context.RaisingContext
