# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class TestPolicyAccount(WeechatOtrTestCase):

    def test_policy_account(self):
        account = weechat_otr.ACCOUNTS['nick@server']

        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            False)
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.html_escape'] = 'on'
        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            True)

    def test_policy_account_non_ascii(self):
        account = weechat_otr.ACCOUNTS['gefährtenick@server']

        self.assertEqual(
            account.getContext('gefährte@server').getPolicy('html_escape'),
            False)
        sys.modules['weechat'].config_options[weechat_otr.PYVER.to_str(
            'otr.policy.server.gefährtenick.html_escape')] = 'on'
        self.assertEqual(
            account.getContext('gefährte@server').getPolicy('html_escape'),
            True)

    def test_policy_account_peer_override(self):
        account = weechat_otr.ACCOUNTS['nick@server']

        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            False)
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.html_escape'] = 'on'
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.friend.html_escape'] = 'off'
        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            False)

    def test_policy_account_peer_override_non_ascii(self):
        account = weechat_otr.ACCOUNTS['gefährtenick@server']

        self.assertEqual(
            account.getContext('gefährte@server').getPolicy('html_escape'),
            False)
        sys.modules['weechat'].config_options[weechat_otr.PYVER.to_str(
            'otr.policy.server.gefährtenick.html_escape')] = 'on'
        sys.modules['weechat'].config_options[weechat_otr.PYVER.to_str(
            'otr.policy.server.gefährtenick.gefährtenick.html_escape')] = 'off'
        self.assertEqual(
            account.getContext('gefährte@server').getPolicy('html_escape'),
            True)
