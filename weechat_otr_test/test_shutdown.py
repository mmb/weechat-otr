# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name

from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase
import weechat_otr_test.mock_account

import weechat_otr

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

    def test_frees_config_section_options(self):
        weechat_otr.shutdown()

        sections = sorted([
            ('color', ),
            ('policy', ),
            ('look', ),
            ('general', )
            ])

        self.assertEqual(
            sections,
            sorted(sys.modules['weechat'].config_section_free_options_calls))

    def test_frees_config_sections(self):
        weechat_otr.shutdown()

        sections = sorted([
            ('color', ),
            ('policy', ),
            ('look', ),
            ('general', )
            ])

        self.assertEqual(
            sections, sorted(sys.modules['weechat'].config_section_free_calls))

    def test_frees_config_file(self):
        weechat_otr.shutdown()

        self.assertEqual(
            [('config file', )], sys.modules['weechat'].config_free_calls)

    def test_removes_bar_item(self):
        weechat_otr.shutdown()
        self.assertEqual(
            [('bar item', )], sys.modules['weechat'].bar_items_removed)

    def test_returns_ok(self):
        self.assertEqual(
            weechat_otr.shutdown(), sys.modules['weechat'].WEECHAT_RC_OK)
