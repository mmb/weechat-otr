# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class CommandStartTestCase(WeechatOtrTestCase):

    def test_start_buffer(self):
        weechat_otr.command_cb(None, 'server_nick2_buffer', 'start')

        self.assertIn(
            (u'', '/quote -server server PRIVMSG nick2 :?OTR?'),
            sys.modules['weechat'].commands)

    def test_start_args(self):
        weechat_otr.command_cb(None, None, 'start nick2 server')

        self.assertIn(
            (u'', '/quote -server server PRIVMSG nick2 :?OTR?'),
            sys.modules['weechat'].commands)

    # /otr refresh is an alias for /otr start

    def test_refresh_buffer(self):
        weechat_otr.command_cb(None, 'server_nick2_buffer', 'refresh')

        self.assertIn(
            (u'', '/quote -server server PRIVMSG nick2 :?OTR?'),
            sys.modules['weechat'].commands)

    def test_refresh_args(self):
        weechat_otr.command_cb(None, None, 'refresh nick2 server')

        self.assertIn(
            (u'', '/quote -server server PRIVMSG nick2 :?OTR?'),
            sys.modules['weechat'].commands)
