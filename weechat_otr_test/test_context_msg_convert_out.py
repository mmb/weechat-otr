# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import sys

import potr

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

from weechat_otr_test import mock_user

import weechat_otr

class ContextMessageConvertOutTestCase(WeechatOtrTestCase):

    def after_setup(self):
        self.context = weechat_otr.IrcContext('account', 'nick@server')
        self.context.user = mock_user.MockUser('user')

    def test_action_encrypted(self):
        self.context.state = potr.context.STATE_ENCRYPTED

        result = self.context.msg_convert_out('\x01ACTION lols\x01')
        self.assertEqual(result, b'/me lols')

    def test_html_escape_on_encrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.user.nick.html_escape'] = 'on'
        self.context.state = potr.context.STATE_ENCRYPTED

        result = self.context.msg_convert_out(
            weechat_otr.PYVER.to_str('< > &'))
        self.assertEqual(result, b'&lt; &gt; &amp;')

    def test_html_escape_on_unencrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.user.nick.html_escape'] = 'on'
        self.context.state = potr.context.STATE_PLAINTEXT

        result = self.context.msg_convert_out(
            weechat_otr.PYVER.to_str('< > &'))
        self.assertEqual(result, b'< > &')

    def test_html_escape_off_encrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.user.nick.html_escape'] = 'off'
        self.context.state = potr.context.STATE_ENCRYPTED

        result = self.context.msg_convert_out(
            weechat_otr.PYVER.to_str('< > &'))
        self.assertEqual(result, b'< > &')

    def test_html_escape_off_unencrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.user.nick.html_escape'] = 'off'
        self.context.state = potr.context.STATE_PLAINTEXT

        result = self.context.msg_convert_out(
            weechat_otr.PYVER.to_str('< > &'))
        self.assertEqual(result, b'< > &')
