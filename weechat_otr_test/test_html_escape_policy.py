# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr_test.recording_account
import weechat_otr

import weechat_otr

class HtmlEscapePolicyTestCase(WeechatOtrTestCase):

    def test_default_html_escape_policy(self):
        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG friend :< > " \' &')
        self.assertEqual(result, 'PRIVMSG friend :< > " \' &')

    def test_html_escape_policy(self):
        sys.modules['weechat'].set_server_current_nick('server', 'nick')
        sys.modules['weechat'].infos.update({
            (weechat_otr.PYVER.to_str('server,nick'),) :
                {'irc_buffer' : 'server_nick_buffer'},
            (weechat_otr.PYVER.to_str('server,nick2'),) :
                {'irc_buffer' : 'server_nick2_buffer'},
            })
        sys.modules['weechat'].buffers.update({
            weechat_otr.PYVER.to_str('server_nick_buffer') : {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick',
                'localvar_server' : 'server',
                },
            weechat_otr.PYVER.to_str('server_nick2_buffer') : {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick2',
                'localvar_server' : 'server',
                },
            })

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

        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.nick2.html_escape'] = 'on'
        self.assertTrue(context2.getPolicy('html_escape'))
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick2.nick.html_filter'] = 'off'
        self.assertFalse(context1.getPolicy('html_filter'))

        weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG nick2 :< > " \' &')

        sys.modules['weechat'].set_server_current_nick('server', 'nick2')
        result = self.send_all('nick', 'nick2', context2.injected)

        self.assertEqual(result, ':nick!user@host PRIVMSG nick2 :&lt; &gt; " \' &amp;')

    def test_html_escape_policy_unencrypted(self):
        nick = 'nick'
        server = 'server'

        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.friend.html_escape'] = 'on'

        result = weechat_otr.message_out_cb(None, None, server,
            ':nick!user@host PRIVMSG friend :< > " \' &')
        self.assertEqual(result, 'PRIVMSG friend :< > " \' &')

    def test_html_escape_policy_non_ascii(self):
        sys.modules['weechat'].set_server_current_nick('server', 'gefährte')
        sys.modules['weechat'].infos.update({
            (weechat_otr.PYVER.to_str('server,gefährte'),) :
                {'irc_buffer' : 'server_nick_buffer'},
            (weechat_otr.PYVER.to_str('server,nick2'),) :
                {'irc_buffer' : 'server_nick2_buffer'},
            })
        sys.modules['weechat'].buffers.update({
            weechat_otr.PYVER.to_str('server_gefährte_buffer') : {
                'localvar_type' : 'private',
                'localvar_channel' : 'gefährte',
                'localvar_server' : 'server',
                },
            weechat_otr.PYVER.to_str('server_nick2_buffer') : {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick2',
                'localvar_server' : 'server',
                },
            })

        account1 = weechat_otr_test.recording_account.RecordingAccount(
            'gefährte@server')
        weechat_otr.ACCOUNTS['gefährte@server'] = account1

        account2 = weechat_otr_test.recording_account.RecordingAccount(
            'nick2@server')
        weechat_otr.ACCOUNTS['nick2@server'] = account2

        context1 = account2.getContext('gefährte@server')
        context2 = account1.getContext('nick2@server')

        weechat_otr.message_in_cb(None, None, 'server',
            ':nick2!user@host PRIVMSG gefährte :?OTRv2?')

        sys.modules['weechat'].set_server_current_nick('server', 'nick2')
        self.send_all('gefährte', 'nick2', context2.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'gefährte')
        self.send_all('nick2', 'gefährte', context1.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'nick2')
        self.send_all('gefährte', 'nick2', context2.injected)

        sys.modules['weechat'].set_server_current_nick('server', 'gefährte')
        self.send_all('nick2', 'gefährte', context1.injected)

        sys.modules['weechat'].config_options[
            'otr.policy.server.gefährte.nick2.html_escape'] = 'on'
        self.assertTrue(context2.getPolicy('html_escape'))
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick2.gefährte.html_filter'] = 'off'
        self.assertFalse(context1.getPolicy('html_filter'))

        weechat_otr.message_out_cb(None, None, 'server',
            ':gefährte!user@host PRIVMSG nick2 :< > " \' &')

        sys.modules['weechat'].set_server_current_nick('server', 'nick2')
        result = self.send_all('gefährte', 'nick2', context2.injected)

        self.assertEqual(result, weechat_otr.PYVER.to_str(':gefährte!user@host PRIVMSG nick2 :&lt; &gt; " \' &amp;'))

    def test_html_escape_policy_non_ascii_unencrypted(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.gefährte.html_escape'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG gefährte :< > " \' &')
        self.assertEqual(result, weechat_otr.PYVER.to_str(
            'PRIVMSG gefährte :< > " \' &'))

    def send_all(self, from_nick, to_nick, messages):
        # pylint: disable=no-self-use
        result = ''
        while True:
            if len(messages) == 0:
                break
            result = weechat_otr.message_in_cb(None, None, 'server',
                ':{from_nick}!user@host PRIVMSG {to_nick} :{message}'.format(
                    from_nick=from_nick,
                    to_nick=to_nick,
                    message=messages.pop().decode('utf-8', 'replace')))
        return result
