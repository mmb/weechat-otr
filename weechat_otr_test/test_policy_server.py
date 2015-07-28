# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

import sys

class TestPolicyServer(WeechatOtrTestCase):

    def test_policy_server(self):
        account = weechat_otr.ACCOUNTS['nick@server']

        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            False)
        sys.modules['weechat'].config_options[
            'otr.policy.server.html_escape'] = 'on'
        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            True)

    def test_policy_server_account_override(self):
        account = weechat_otr.ACCOUNTS['nick@server']

        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            False)
        sys.modules['weechat'].config_options[
            'otr.policy.server.html_escape'] = 'on'
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.html_escape'] = 'off'
        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            False)

    def test_policy_server_peer_override(self):
        account = weechat_otr.ACCOUNTS['nick@server']

        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            False)
        sys.modules['weechat'].config_options[
            'otr.policy.server.html_escape'] = 'on'
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.friend.html_escape'] = 'off'
        self.assertEqual(
            account.getContext('friend@server').getPolicy('html_escape'),
            False)
