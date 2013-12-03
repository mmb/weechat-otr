# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

import sys
import unittest

import mock_weechat
sys.modules['weechat'] = mock_weechat.MockWeechat()

import weechat_otr

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
        self.assertEqual(result, ':f PRIVMSG t :line1\r\n:f PRIVMSG t :line2')

    def test_build_privmsg_out_without_newline(self):
        result = weechat_otr.build_privmsg_out('t', 'line1')
        self.assertEqual(result, 'PRIVMSG t :line1')

    def test_build_privmsg_out_with_newline(self):
        result = weechat_otr.build_privmsg_out('t', 'line1\nline2')
        self.assertEqual(result, 'PRIVMSG t :line1\r\nPRIVMSG t :line2')

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
