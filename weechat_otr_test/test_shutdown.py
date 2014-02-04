# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase
import weechat_otr_test.mock_account

import weechat_otr

import sys
import unittest

class ShutdownTestCase(WeechatOtrTestCase):

    def test_writes_config(self):
        weechat_otr.shutdown()
        self.assertEqual(
            [('config file', )], sys.modules['weechat'].config_written)

    def test_ends_all_private(self):
        account1 = weechat_otr_test.mock_account.MockAccount()
        account2 = weechat_otr_test.mock_account.MockAccount()

        weechat_otr.ACCOUNTS['account1'] = account1
        weechat_otr.ACCOUNTS['account2'] = account2

        weechat_otr.shutdown()
        self.assertEqual(account1.end_all_privates, 1)
        self.assertEqual(account2.end_all_privates, 1)

    @unittest.skip('write me')
    def test_frees_all_config(self):
        pass

    def test_removes_bar_item(self):
        weechat_otr.shutdown()
        self.assertEqual(
            [('bar item', )], sys.modules['weechat'].bar_items_removed)

    def test_returns_ok(self):
        self.assertEqual(
            weechat_otr.shutdown(), sys.modules['weechat'].WEECHAT_RC_OK)
