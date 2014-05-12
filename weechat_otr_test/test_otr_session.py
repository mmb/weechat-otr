# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.session_test_case import SessionTestCase

import weechat_otr_test.recording_account
import weechat_otr

import sys

class OtrSessionTestCase(SessionTestCase):

    def test_otr_session(self):
        sys.modules['weechat'].set_server_current_nick('server', 'nick')

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

    def test_otr_session_non_ascii(self):
        sys.modules['weechat'].set_server_current_nick('server', 'gefährte')
        sys.modules['weechat'].infos.update({
            (weechat_otr.PYVER.to_str('server,gefährte'),) :
                {'irc_buffer' : 'server_gefährte_buffer'},
            (weechat_otr.PYVER.to_str('server,gefährte2'),) :
                {'irc_buffer' : 'server_gefährte2_buffer'},
            })
        sys.modules['weechat'].buffers.update({
            weechat_otr.PYVER.to_str('server_gefährte_buffer') : {
                'localvar_type' : 'private',
                'localvar_channel' : 'gefährte',
                'localvar_server' : 'server',
                },
            weechat_otr.PYVER.to_str('server_gefährte2_buffer') : {
                'localvar_type' : 'private',
                'localvar_channel' : 'gefährte2',
                'localvar_server' : 'server',
                },
            })

        account1 = weechat_otr_test.recording_account.RecordingAccount(
            'gefährte@server')
        weechat_otr.ACCOUNTS['gefährte@server'] = account1

        account2 = weechat_otr_test.recording_account.RecordingAccount(
            'gefährte2@server')
        weechat_otr.ACCOUNTS['gefährte2@server'] = account2

        context1 = account2.getContext('gefährte@server')
        context2 = account1.getContext('gefährte2@server')

        weechat_otr.message_in_cb(None, None, 'server',
            ':gefährte2!user@host PRIVMSG gefährte :?OTRv2?')

        sys.modules['weechat'].set_server_current_nick('server', 'gefährte2')
        self.send_all('gefährte', 'gefährte2', context2.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'gefährte')
        self.send_all('gefährte2', 'gefährte', context1.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'gefährte2')
        self.send_all('gefährte', 'gefährte2', context2.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'gefährte')
        self.send_all('gefährte2', 'gefährte', context1.injected)

        self.assertTrue(context1.is_encrypted())
        self.assertTrue(context2.is_encrypted())

        weechat_otr.message_out_cb(None, None, 'server',
            ':gefährte!user@host PRIVMSG gefährte2 :hi')

        sys.modules['weechat'].set_server_current_nick('server', 'gefährte2')

        result = weechat_otr.message_in_cb(None, None, 'server',
            ':gefährte!user@host PRIVMSG gefährte2 :%s' % \
            context2.injected.pop())

        self.assertEqual(result, weechat_otr.PYVER.to_str(
            ':gefährte!user@host PRIVMSG gefährte2 :hi'))
