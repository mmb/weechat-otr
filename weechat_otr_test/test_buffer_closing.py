
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

import weechat_otr_test.mock_account
import weechat_otr_test.mock_context

import sys

class BufferClosedTestCase(WeechatOtrTestCase):

    def test_callback_registered(self):
        self.assertIn(
            ('buffer_closing', 'buffer_closing_cb', ''),
            sys.modules['weechat'].hook_signals)

    def test_session_ended(self):
        context = weechat_otr_test.mock_context.MockContext()
        account = weechat_otr_test.mock_account.MockAccount()
        account.add_context('nick2@server', context)
        weechat_otr.ACCOUNTS['nick@server'] = account

        weechat_otr.buffer_closing_cb(None, None, 'server_nick2_buffer')

        self.assertEqual(context.disconnects, 1)
