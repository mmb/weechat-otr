# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr_test.recording_account
import weechat_otr

import sys

class OtrSessionTestCase(WeechatOtrTestCase):

    def test_otr_session(self):
        account1 = weechat_otr_test.recording_account.RecordingAccount(
            'nick@server')
        weechat_otr.ACCOUNTS['nick@server'] = account1

        account2 = weechat_otr_test.recording_account.RecordingAccount(
            'nick2@server')
        weechat_otr.ACCOUNTS['nick2@server'] = account2

        context1 = account2.getContext('nick@server')
        context2 = account1.getContext('nick2@server')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick2!user@host PRIVMSG nick :?OTRv2?')

        sys.modules['weechat'].set_server_current_nick('server', 'nick2')
        self.send_all('nick', 'nick2', context2.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'nick')
        self.send_all('nick2', 'nick', context1.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'nick2')
        self.send_all('nick', 'nick2', context2.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'nick')
        self.send_all('nick2', 'nick', context1.injected)

        self.assertTrue(context1.is_encrypted())
        self.assertTrue(context2.is_encrypted())

        weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG nick2 :hi')

        sys.modules['weechat'].set_server_current_nick('server', 'nick2')

        result = weechat_otr.message_in_cb(None, None, 'server',
            ':nick!user@host PRIVMSG nick2 :%s' % context2.injected.pop())

        self.assertEqual(result, ':nick!user@host PRIVMSG nick2 :hi')

    def send_all(self, from_nick, to_nick, messages):
        # pylint: disable=no-self-use
        while True:
            if len(messages) == 0:
                break
            weechat_otr.message_in_cb(None, None, 'server',
                ':{from_nick}!user@host PRIVMSG {to_nick} :{message}'.format(
                    from_nick=from_nick,
                    to_nick=to_nick,
                    message=messages.pop().decode('utf-8', 'replace')))
