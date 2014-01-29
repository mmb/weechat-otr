# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import os
import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class KeyGenerationTestCase(WeechatOtrTestCase):

    def test_creates_key_file(self):
        sys.modules['weechat'].set_server_current_nick('server', 'noob')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG noob :?OTRv2?')

        key_path = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'noob@server.key3')

        self.assertGreater(os.path.getsize(key_path), 0)

    def test_creates_key_file_non_ascii(self):
        sys.modules['weechat'].set_server_current_nick('server', 'gefährte')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG gefährte :?OTRv2?')

        key_path = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'gefährte@server.key3')

        self.assertGreater(os.path.getsize(key_path), 0)
