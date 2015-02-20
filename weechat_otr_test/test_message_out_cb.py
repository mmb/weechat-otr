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

    def test_message_out_cb_send_tag_alis(self):
        self.assertNickIsNotTagged('Alis')

    def test_message_out_cb_send_tag_botserv(self):
        self.assertNickIsNotTagged('BotServ')

    def test_message_out_cb_send_tag_chanfix(self):
        self.assertNickIsNotTagged('ChanFix')

    def test_message_out_cb_send_tag_chanserv(self):
        self.assertNickIsNotTagged('ChanServ')

    def test_message_out_cb_send_tag_gameserv(self):
        self.assertNickIsNotTagged('GameServ')

    def test_message_out_cb_send_tag_global(self):
        self.assertNickIsNotTagged('Global')

    def test_message_out_cb_send_tag_groupserv(self):
        self.assertNickIsNotTagged('GroupServ')

    def test_message_out_cb_send_tag_helpserv(self):
        self.assertNickIsNotTagged('HelpServ')

    def test_message_out_cb_send_tag_hostserv(self):
        self.assertNickIsNotTagged('HostServ')

    def test_message_out_cb_send_tag_infoserv(self):
        self.assertNickIsNotTagged('InfoServ')

    def test_message_out_cb_send_tag_memoserv(self):
        self.assertNickIsNotTagged('MemoServ')

    def test_message_out_cb_send_tag_nickserv(self):
        self.assertNickIsNotTagged('NickServ')

    def test_message_out_cb_send_tag_operserv(self):
        self.assertNickIsNotTagged('OperServ')

    def test_message_out_cb_send_tag_rpgserv(self):
        self.assertNickIsNotTagged('RpgServ')

    def test_message_out_cb_send_tag_statserv(self):
        self.assertNickIsNotTagged('StatServ')

    def test_message_out_cb_send_tag_saslserv(self):
        self.assertNickIsNotTagged('SaslServ')

    def test_message_out_cb_send_tag_star(self):
        self.assertNickIsNotTagged('*man')

    def test_message_out_cb_send_tag_ctcp(self):
        sys.modules['weechat'].config_options[
            'otr.policy.default.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG friend :\x01CTCP VERSION\x01')
        self.assertEqual(weechat_otr.PYVER.to_unicode(result),
            'PRIVMSG friend :\x01CTCP VERSION\x01')

    def test_message_out_cb_no_send_tag_regex_non_ascii(self):
        sys.modules['weechat'].config_options[
            'otr.general.no_send_tag_regex'] = \
            weechat_otr.PYVER.to_str('^gefährte$')

        self.assertNickIsNotTagged('gefährte')

    def test_message_out_cb_empty_no_send_tag_regex(self):
        sys.modules['weechat'].config_options[
            'otr.policy.default.send_tag'] = 'on'
        sys.modules['weechat'].config_options[
            'otr.general.no_send_tag_regex'] = weechat_otr.PYVER.to_str('')

        result = weechat_otr.message_out_cb(None, None, 'server',
            weechat_otr.PYVER.to_str(":nick!user@host PRIVMSG friend :hi"))
        self.assertEqual(weechat_otr.PYVER.to_unicode(result),
            "PRIVMSG friend :hi \t  \t\t\t\t \t \t \t    \t\t  \t \t")

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

    def assertNickIsNotTagged(self, nick):
        sys.modules['weechat'].config_options[
            'otr.policy.default.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            weechat_otr.PYVER.to_str(
            ':nick!user@host PRIVMSG {nick} :send friend hi'.format(
            nick=nick)))
        self.assertEqual(weechat_otr.PYVER.to_unicode(result),
            'PRIVMSG {nick} :send friend hi'.format(nick=nick))
