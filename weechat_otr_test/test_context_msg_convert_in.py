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

class ContextMessageConvertInTestCase(WeechatOtrTestCase):

    def after_setup(self):
        self.context = weechat_otr.IrcContext('account', 'nick@server')
        self.context.user = mock_user.MockUser('user')

    def test_unicode(self):
        result = self.context.msg_convert_in(weechat_otr.PYVER.to_str('hi'))
        self.assertEqual(result, 'hi')

    def test_html_filter_on_encrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.user.nick.html_filter'] = 'on'
        self.context.state = potr.context.STATE_ENCRYPTED

        result = self.context.msg_convert_in(
            weechat_otr.PYVER.to_str('<font>lol</font><br/>&lt;&gt;'))
        self.assertEqual(result, 'lol\n<>')

    def test_html_filter_on_unencrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.user.nick.html_filter'] = 'on'
        self.context.state = potr.context.STATE_PLAINTEXT

        result = self.context.msg_convert_in(
            weechat_otr.PYVER.to_str('<font>lol</font><br/>&lt;&gt;'))
        self.assertEqual(result, '<font>lol</font><br/>&lt;&gt;')

    def test_html_filter_off_encrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.user.nick.html_filter'] = 'off'
        self.context.state = potr.context.STATE_ENCRYPTED

        result = self.context.msg_convert_in(
            weechat_otr.PYVER.to_str('<font>lol</font><br/>&lt;&gt;'))
        self.assertEqual(result, '<font>lol</font><br/>&lt;&gt;')

    def test_html_filter_off_unencrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.user.nick.html_filter'] = 'off'
        self.context.state = potr.context.STATE_PLAINTEXT

        result = self.context.msg_convert_in(
            weechat_otr.PYVER.to_str('<font>lol</font><br/>&lt;&gt;'))
        self.assertEqual(result, '<font>lol</font><br/>&lt;&gt;')

    def test_action_encrypted(self):
        self.context.state = potr.context.STATE_ENCRYPTED

        result = self.context.msg_convert_in(
            weechat_otr.PYVER.to_str('/me lols'))
        self.assertEqual(result, '\x01ACTION lols\x01')

    def test_action_unencrypted(self):
        self.context.state = potr.context.STATE_PLAINTEXT

        result = self.context.msg_convert_in(
            weechat_otr.PYVER.to_str('/me lols'))
        self.assertEqual(result, '/me lols')
