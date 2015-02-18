# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import os
import re
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

    def test_creates_key_file_from_default_key(self):
        sys.modules['weechat'].set_server_current_nick('server', 'noob')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG noob :?OTRv2?')

        sys.modules['weechat'].config_options[
            'otr.general.defaultkey'] = 'noob@server'

        sys.modules['weechat'].set_server_current_nick('server', 'noob2')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG noob2 :?OTRv2?')

        noob_key_path = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'noob@server.key3')

        noob2_key_path = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'noob2@server.key3')

        with open(noob_key_path, 'rb') as noob_key:
            with open(noob2_key_path, 'rb') as noob2_key:
                self.assertEqual(noob_key.read(), noob2_key.read())

    def test_preserves_existing_keys_if_default_key(self):
        sys.modules['weechat'].set_server_current_nick('server', 'noob2')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG noob2 :?OTRv2?')

        account = weechat_otr.ACCOUNTS['noob2@server']
        orig_noob2_priv_key = account.getPrivkey()

        sys.modules['weechat'].set_server_current_nick('server', 'noob')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG noob :?OTRv2?')

        sys.modules['weechat'].config_options[
            'otr.general.defaultkey'] = 'noob@server'

        account.privkey = None

        sys.modules['weechat'].set_server_current_nick('server', 'noob2')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG noob2 :?OTRv2?')

        self.assertEqual(account.privkey, orig_noob2_priv_key)

    def test_reads_key_file(self):
        sys.modules['weechat'].set_server_current_nick('server', 'noob')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG noob :?OTRv2?')

        account = weechat_otr.ACCOUNTS['noob@server']
        priv_key = account.getPrivkey()
        account.privkey = None

        self.assertEqual(priv_key, account.getPrivkey())
