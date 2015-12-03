# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class IrcUserTestCase(WeechatOtrTestCase):

    def test_irc_user(self):
        self.assertEqual(weechat_otr.irc_user('nick', 'server'), 'nick@server')

    def test_irc_user_case_insensitive(self):
        self.assertEqual(weechat_otr.irc_user('NiCk', 'server'), 'nick@server')
