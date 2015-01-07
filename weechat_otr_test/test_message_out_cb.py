# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class MessageOutCbTestCase(WeechatOtrTestCase):

    def test_message_out_cb(self):
        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG friend :hello')
        self.assertEqual(result, 'PRIVMSG friend :hello')

    def test_message_out_cb_send_tag_non_ascii(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.friend.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            ":nick!user@host PRIVMSG friend :\xc3")
        self.assertEqual(weechat_otr.PYVER.to_unicode(result),
            "PRIVMSG friend :\xc3 \t  \t\t\t\t \t \t \t    \t\t  \t \t")

    def test_message_out_cb_send_tag_chanserv(self):
        sys.modules['weechat'].config_options[
            'otr.policy.default.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG ChanServ :register channel secret desc')
        self.assertEqual(weechat_otr.PYVER.to_unicode(result),
            'PRIVMSG ChanServ :register channel secret desc')

    def test_message_out_cb_send_tag_memoserv(self):
        sys.modules['weechat'].config_options[
            'otr.policy.default.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG MemoServ :send friend hi')
        self.assertEqual(weechat_otr.PYVER.to_unicode(result),
            'PRIVMSG MemoServ :send friend hi')

    def test_message_out_cb_send_tag_nickserv(self):
        sys.modules['weechat'].config_options[
            'otr.policy.default.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            ":nick!user@host PRIVMSG NickServ :identify secret")
        self.assertEqual(weechat_otr.PYVER.to_unicode(result),
            "PRIVMSG NickServ :identify secret")

    def test_message_out_cb_nick_with_at(self):
        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG @#chan :hello')
        self.assertEqual(result, ':nick!user@host PRIVMSG @#chan :hello')

    def test_otr_disabled_require_encryption(self):
        sys.modules['weechat'].config_options.update({
            'otr.policy.default.allow_v2' : 'off',
            'otr.policy.default.require_encryption' : 'on'
        })

        weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG nick2 :hello')

        self.assertNotPrinted('server_nick2_buffer',
            'eval(${color:default}:! ${color:brown}otr${color:default} !:)\t'
            '(color lightred)Your message will not be sent, because policy '
            'requires an encrypted connection.')
        self.assertNotPrinted('server_nick2_buffer',
            'eval(${color:default}:! ${color:brown}otr${color:default} !:)\t'
            '(color lightblue)Wait for the OTR connection or change the '
            'policy to allow clear-text messages:\r\n(color '
            'lightblue)/policy set require_encryption off')
