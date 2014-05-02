# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class MessageOutCbTestCase(WeechatOtrTestCase):

    def test_message_out_cb_nick_with_at(self):
        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG @#chan :hello')
        self.assertEqual(result, 'PRIVMSG @#chan :hello')
