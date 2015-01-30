# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class ParseIrcPrivmsgTestCase(WeechatOtrTestCase):

    def test_parse_irc_privmsg_nick(self):
        result = weechat_otr.parse_irc_privmsg(
            ':nick!user@host PRIVMSG nick2 :the message', 'server')

        self.assertEqual(result, {
            'from': 'nick!user@host',
            'from_nick': 'nick',
            'to': 'nick2',
            'to_channel': None,
            'to_nick': 'nick2',
            'text': 'the message'
            })

    def test_parse_irc_privmsg_channel_ampersand(self):
        sys.modules['weechat'].infos[
            ('server,CHANTYPES',)][
            'irc_server_isupport_value'] += '&'

        result = weechat_otr.parse_irc_privmsg(
            ':nick!user@host PRIVMSG &channel :test', 'server')
        self.assertEqual(result['to_channel'], '&channel')

    def test_parse_irc_privmsg_non_ascii(self):
        sys.modules['weechat'].info_hashtables = {
            'irc_message_parse' : [{
                'arguments': weechat_otr.PYVER.to_str('nick2\xc3 :\xc3'),
                'channel': weechat_otr.PYVER.to_str('nick2\xc3'),
                'command': weechat_otr.PYVER.to_str('PRIVMSG'),
                'host': weechat_otr.PYVER.to_str('nick\xc3!user@host'),
                'nick': weechat_otr.PYVER.to_str('nick\xc3'),
            }]
        }

        result = weechat_otr.parse_irc_privmsg(
            ':nick\xc3!user@host PRIVMSG nick2\xc3 :\xc3', 'server')

        self.assertEqual(result, {
            'from': 'nick\xc3!user@host',
            'from_nick': 'nick\xc3',
            'to': 'nick2\xc3',
            'to_channel': None,
            'to_nick': 'nick2\xc3',
            'text': '\xc3'
            })

    def test_parse_irc_privmsg_nick_no_colon(self):
        result = weechat_otr.parse_irc_privmsg(
            ':nick!user@host PRIVMSG nick2 test', 'server')

        self.assertEqual(result, {
            'from': 'nick!user@host',
            'from_nick': 'nick',
            'to': 'nick2',
            'to_channel': None,
            'to_nick': 'nick2',
            'text': 'test'
            })

    def test_parse_irc_privmsg_nick_no_colon_spaces(self):
        result = weechat_otr.parse_irc_privmsg(
            ':nick!user@host PRIVMSG nick2 the message', 'server')

        self.assertEqual(result, {
            'from': 'nick!user@host',
            'from_nick': 'nick',
            'to': 'nick2',
            'to_channel': None,
            'to_nick': 'nick2',
            'text': 'the message'
            })

    def test_parse_irc_privmsg_not_privmsg(self):
        with self.assertRaises(weechat_otr.PrivmsgParseException):
            weechat_otr.parse_irc_privmsg(
            ':nick!user@host OTHERCOMMAND nick2 the message', 'server')

    def test_parse_irc_privmsg_command_case_insensitive(self):
        result = weechat_otr.parse_irc_privmsg(
            ':nick!user@host privmsg nick2 :the message', 'server')

        self.assertEqual(result, {
            'from': 'nick!user@host',
            'from_nick': 'nick',
            'to': 'nick2',
            'to_channel': None,
            'to_nick': 'nick2',
            'text': 'the message'
            })

    def test_parse_irc_privmsg_no_from(self):
        result = weechat_otr.parse_irc_privmsg(
            'PRIVMSG nickserv :identify secret', 'server')

        self.assertEqual(result, {
            'from': '',
            'from_nick': '',
            'to': 'nickserv',
            'to_channel': None,
            'to_nick': 'nickserv',
            'text': 'identify secret'
            })

    def test_parse_irc_privmsg_to_self(self):
        result = weechat_otr.parse_irc_privmsg(
            ':nick!user@host PRIVMSG nick :the message', 'server')

        self.assertEqual(result, {
            'from': 'nick!user@host',
            'from_nick': 'nick',
            'to': 'nick',
            'to_channel': None,
            'to_nick': 'nick',
            'text': 'the message'
            })
