# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import platform
import sys

import potr

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

    def test_message_out_cb_send_tag_ctcp(self):
        sys.modules['weechat'].config_options[
            'otr.policy.default.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG friend :\x01CTCP VERSION\x01')
        self.assertEqual(weechat_otr.PYVER.to_unicode(result),
            'PRIVMSG friend :\x01CTCP VERSION\x01')

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

    def test_exception_raised_returns_empty_string(self):
        sys.modules['weechat'].info_get_hashtable_raise = Exception('test')

        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG nick2 :hello')
        self.assertEqual(result, '')

    def test_exception_raised_prints_traceback(self):
        sys.modules['weechat'].info_get_hashtable_raise = Exception('test')

        weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG nick2 :hello')
        self.assertPrintedContains('', 'Exception: test')

    def test_exception_raised_prints_versions(self):
        sys.modules['weechat'].info_get_hashtable_raise = Exception('test')
        sys.modules['weechat'].infos[('',)]['version'] = '9.8.7'

        version_str = (
            'Versions: weechat-otr {script_version}, '
            'potr {potr_major}.{potr_minor}.{potr_patch}-{potr_sub}, '
            'Python {python_version}, '
            'WeeChat 9.8.7'
            ).format(
            script_version=weechat_otr.SCRIPT_VERSION,
            potr_major=potr.VERSION[0],
            potr_minor=potr.VERSION[1],
            potr_patch=potr.VERSION[2],
            potr_sub=potr.VERSION[3],
            python_version=platform.python_version())

        weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG nick2 :hello')
        self.assertPrintedContains('', version_str)
