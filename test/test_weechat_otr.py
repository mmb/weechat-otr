# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

import sys
import unittest

import mock_weechat
sys.modules['weechat'] = mock_weechat.MockWeechat()

import weechat_otr

import mock_account
import mock_context

class WeechatOtrTestCase(unittest.TestCase):

    def setUp(self):
        sys.modules['weechat'].save()
        self.afterSetUp()

    def tearDown(self):
        sys.modules['weechat'].restore()
        self.afterTearDown()

    def afterSetUp(self):
        pass

    def afterTearDown(self):
        pass

class WeechatOtrGeneralTestCase(WeechatOtrTestCase):

    def test_message_out_cb(self):
        result = weechat_otr.message_out_cb(None, None, 'server',
            ':nick!user@host PRIVMSG friend :hello')
        self.assertEqual(result, 'PRIVMSG friend :hello')

    def test_message_out_cb_send_tag_non_ascii(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.friend.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'server',
            ":nick!user@host PRIVMSG friend :\xc3")
        self.assertEqual(result,
            "PRIVMSG friend :\xef\xbf\xbd \t  \t\t\t\t \t \t \t    \t\t  \t \t")

    def test_parse_irc_privmsg_channel_ampersand(self):
        result = weechat_otr.parse_irc_privmsg(
            ':nick!user@host PRIVMSG &channel :test')
        self.assertEqual(result['to_channel'], '&channel')

    def test_build_privmsg_in_without_newline(self):
        result = weechat_otr.build_privmsg_in('f', 't', 'line1')
        self.assertEqual(result, ':f PRIVMSG t :line1')

    def test_build_privmsg_in_with_newline(self):
        result = weechat_otr.build_privmsg_in('f', 't', 'line1\nline2')
        self.assertEqual(result, ':f PRIVMSG t :line1line2')

    def test_build_privmsgs_in_without_newline(self):
        fromm  = 'f'
        to     = 't'
        line   = 'line1'
        result = weechat_otr.build_privmsgs_in(fromm, to, line)
        self.assertEqual(result,
                weechat_otr.build_privmsg_in(fromm, to, line))

    def test_build_privmsgs_in_without_newline_prefix(self):
        fromm  = 'f'
        to     = 't'
        line   = 'line1'
        prefix = 'Some prefix: '
        result = weechat_otr.build_privmsgs_in(fromm, to, line, prefix)
        self.assertEqual(result,
                weechat_otr.build_privmsg_in(fromm, to, prefix+line))

    def test_build_privmsgs_in_with_newline(self):
        fromm  = 'f'
        to     = 't'
        result = weechat_otr.build_privmsgs_in(fromm, to, 'line1\nline2')
        self.assertEqual(result, '{msg1}\r\n{msg2}'.format(
            msg1 = weechat_otr.build_privmsg_in(fromm, to, 'line1'),
            msg2 = weechat_otr.build_privmsg_in(fromm, to, 'line2')))

    def test_build_privmsgs_in_with_newline_prefix(self):
        fromm  = 'f'
        to     = 't'
        prefix = 'Some prefix: '
        result = weechat_otr.build_privmsgs_in(fromm, to, 'line1\nline2',
                prefix)
        self.assertEqual(result, '{msg1}\r\n{msg2}'.format(
            msg1 = weechat_otr.build_privmsg_in(fromm, to,
                '{}line1'.format(prefix)),
            msg2 = weechat_otr.build_privmsg_in(fromm, to,
                '{}line2'.format(prefix))))

    def test_build_privmsg_out_without_newline(self):
        result = weechat_otr.build_privmsg_out('t', 'line1')
        self.assertEqual(result, 'PRIVMSG t :line1')

    def test_build_privmsg_out_with_newline(self):
        result = weechat_otr.build_privmsg_out('t', 'line1\nline2')
        self.assertEqual(result, 'PRIVMSG t :line1\r\nPRIVMSG t :line2')

    def test_msg_irc_from_plain_action(self):
        result = weechat_otr.msg_irc_from_plain('/me does something')
        self.assertEqual(result,
                '\x01ACTION does something\x01')

    def test_msg_irc_from_plain_no_action(self):
        msg_no_action = 'just a message'
        self.assertEqual(weechat_otr.msg_irc_from_plain(msg_no_action),
                msg_no_action)

    def test_msg_irc_from_plain_action_invariant(self):
        msg_action = '\x01ACTION does something\x01'
        self.assertEqual(msg_action,
                weechat_otr.msg_irc_from_plain(
                    weechat_otr.msg_plain_from_irc(msg_action)
                    )
                )

    def test_msg_plain_from_irc_action(self):
        result = weechat_otr.msg_plain_from_irc('\x01ACTION does something\x01')
        self.assertEqual(result,
                '/me does something')

    def test_msg_plain_from_irc_no_action(self):
        msg_no_action = 'just a message'
        self.assertEqual(weechat_otr.msg_plain_from_irc(msg_no_action),
                msg_no_action)

    def test_msg_plain_from_irc_action_invariant(self):
        msg_action = '/me does something'
        self.assertEqual(msg_action,
                weechat_otr.msg_plain_from_irc(
                    weechat_otr.msg_irc_from_plain(msg_action)
                    )
                )

    def test_command_cb_start_send_tag_off(self):
        weechat_otr.command_cb(None, None, 'start')

        self.assertPrinted('server_nick_buffer',
          'otr\tSending OTR query... Please await confirmation of the OTR ' +
          'session being started before sending a message.')

        self.assertPrinted('server_nick_buffer',
          'otr\tTo try OTR on all conversations with nick@server: /otr ' +
          'policy send_tag on')

    def test_command_cb_start_send_tag_off_no_hints(self):
        sys.modules['weechat'].config_options[
            'otr.general.hints'] = 'off'
        weechat_otr.command_cb(None, None, 'start')

        self.assertNotPrinted('server_nick_buffer',
            'otr\tTo try OTR on all conversations with nick@server: /otr ' +
            'policy send_tag on')

    def test_command_cb_start_send_tag_off_with_hints(self):
        sys.modules['weechat'].config_options['otr.general.hints'] = 'on'
        weechat_otr.command_cb(None, None, 'start')

        self.assertPrinted('server_nick_buffer',
            'otr\tTo try OTR on all conversations with nick@server: /otr ' +
            'policy send_tag on')

    def test_command_cb_start_send_tag_on(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.nick.send_tag'] = 'on'
        weechat_otr.command_cb(None, None, 'start')

        self.assertPrinted('server_nick_buffer',
          'otr\tSending OTR query... Please await confirmation of the OTR ' +
          'session being started before sending a message.')

    def test_irc_sanitize(self):
        result = weechat_otr.irc_sanitize(
            'this\r\x00 is \r\n\rnot an i\n\x00rc command')
        self.assertEqual(result, 'this is not an irc command')

    def test_print_buffer_not_private(self):
        weechat_otr.command_cb(None, None, 'start no_window_nick server')
        self.assertPrinted('non_private_buffer',
            'otr\t[no_window_nick] Sending OTR query... Please await ' +
            'confirmation of the OTR session being started before sending a ' +
            'message.')

    def test_smp_ask_nick_server_question_secret(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(
            None, None, 'smp ask nick2 server question secret')

        self.assertEqual(('secret', 'question'), context.smp_init)

    def test_smp_ask_nick_server_secret(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(
            None, None, 'smp ask nick2 server secret')

        self.assertEqual(('secret', None), context.smp_init)

    def test_smp_ask_question_secret(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(
            None, 'server_nick2_buffer', 'smp ask question secret')

        self.assertEqual(('secret', 'question'), context.smp_init)

    def test_smp_ask_secret(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(None, 'server_nick2_buffer', 'smp ask secret')

        self.assertEqual(('secret', None), context.smp_init)

    def test_smp_ask_nick_server_question_secret_multiple_words(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(
            None, None, "smp ask nick2 server 'what is the secret?' "
            "'eastmost penninsula is the secret'")

        self.assertEqual(
            ('eastmost penninsula is the secret', 'what is the secret?'),
            context.smp_init)

    def setup_smp_context(self, account_name, context_name):
        context = mock_context.MockContext()
        account = mock_account.MockAccount()
        account.add_context(context_name, context)
        weechat_otr.ACCOUNTS[account_name] = account

        return context

    def assertPrinted(self, buf, text):
        self.assertIn(text, sys.modules['weechat'].printed[buf])

    def assertNotPrinted(self, buf, text):
        self.assertNotIn(text, sys.modules['weechat'].printed.get(buf, []))

class AssemblerTestCase(WeechatOtrTestCase):

    def afterSetUp(self):
        self.assembler = weechat_otr.Assembler()

    def test_is_query_start(self):
        self.assembler.add('?OTRv2? encryption?')

        self.assertTrue(self.assembler.is_query())

    def test_is_query_middle(self):
        self.assembler.add('ATT: ?OTRv2?someone requested encryption!')

        self.assertTrue(self.assembler.is_query())

    def test_is_query_end(self):
        self.assembler.add('encryption? ?OTRv2?')

        self.assertTrue(self.assembler.is_query())
