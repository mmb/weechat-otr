# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.session_test_case import SessionTestCase

import weechat_otr_test.recording_account
import weechat_otr

import sys

class OtrSessionTestCase(SessionTestCase):

    def test_log_level_return_to_default(self):
        sys.modules['weechat'].set_server_current_nick('server', 'nick')

        account1 = weechat_otr_test.recording_account.RecordingAccount(
            'nick@server')
        weechat_otr.ACCOUNTS['nick@server'] = account1

        account2 = weechat_otr_test.recording_account.RecordingAccount(
            'nick2@server')
        weechat_otr.ACCOUNTS['nick2@server'] = account2

        context1 = account2.getContext('nick@server')
        context2 = account1.getContext('nick2@server')

        sys.modules['weechat'].infolists = {
            ('logger_buffer', '', '') : [
                {
                    'pointer' : {'buffer' : context1.buffer()},
                    'integer' : {
                        'log_enabled' : 1,
                        'log_level' : 0,
                    },
                }
            ],
        }

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

        context1.disconnect()

        self.assertIn(
            ('server_nick_buffer',
                '/mute unset logger.level.irc.server_nick_buffer_name'),
            sys.modules['weechat'].commands)

    def test_log_level_return_to_previous(self):
        sys.modules['weechat'].config_options[
            'logger.level.irc.server_nick_buffer_name'] = 2

        sys.modules['weechat'].set_server_current_nick('server', 'nick')

        account1 = weechat_otr_test.recording_account.RecordingAccount(
            'nick@server')
        weechat_otr.ACCOUNTS['nick@server'] = account1

        account2 = weechat_otr_test.recording_account.RecordingAccount(
            'nick2@server')
        weechat_otr.ACCOUNTS['nick2@server'] = account2

        context1 = account2.getContext('nick@server')
        context2 = account1.getContext('nick2@server')

        sys.modules['weechat'].infolists = {
            ('logger_buffer', '', '') : [
                {
                    'pointer' : {'buffer' : context1.buffer()},
                    'integer' : {
                        'log_enabled' : 1,
                        'log_level' : 2,
                    },
                }
            ],
        }

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

        context1.disconnect()

        self.assertIn(
            ('server_nick_buffer', '/mute logger set 2'),
            sys.modules['weechat'].commands)
