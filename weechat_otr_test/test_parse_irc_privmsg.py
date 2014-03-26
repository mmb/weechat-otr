# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class WeechatOtrGeneralTestCase(WeechatOtrTestCase):

    def test_parse_irc_privmsg_non_ascii(self):
        sys.modules['weechat'].info_hashtables = {
            'irc_message_parse' : [{
                'arguments': weechat_otr.PYVER.to_str('nick2\xc3 :\xc3'),
                'command': weechat_otr.PYVER.to_str('PRIVMSG'),
                'host': weechat_otr.PYVER.to_str('nick\xc3!user@host'),
                'nick': weechat_otr.PYVER.to_str('nick\xc3'),
            }]
        }

        result = weechat_otr.parse_irc_privmsg(
            ':nick\xc3!user@host PRIVMSG nick2\xc3 :\xc3')

        self.assertEqual(result, {
            'from': 'nick\xc3!user@host',
            'from_nick': 'nick\xc3',
            'to': 'nick2\xc3',
            'to_channel': None,
            'to_nick': 'nick2\xc3',
            'text': '\xc3'
            })
