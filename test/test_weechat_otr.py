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

    def tearDown(self):
        sys.modules['weechat'].restore()

    def test_message_out_cb(self):
        result = weechat_otr.message_out_cb(None, None, 'freenode',
            ':nick!user@host PRIVMSG friend :hello')
        self.assertEquals(result, 'PRIVMSG friend :hello')

    def test_message_out_cb_send_tag_non_ascii(self):
        sys.modules['weechat'].config_options[
            'otr.policy.freenode.nick.friend.send_tag'] = 'on'

        result = weechat_otr.message_out_cb(None, None, 'freenode',
            ":nick!user@host PRIVMSG friend :\xc3")
        self.assertEquals(result,
            "PRIVMSG friend :\xef\xbf\xbd \t  \t\t\t\t \t \t \t    \t\t  \t \t")

    def test_parse_irc_privmsg_channel_ampersand(self):
        result = weechat_otr.parse_irc_privmsg(
            ':nick!user@host PRIVMSG &channel :test')
        self.assertEquals(result['to_channel'], '&channel')

    def test_build_privmsg_in_without_newline(self):
        result = weechat_otr.build_privmsg_in('f', 't', 'line1')
        self.assertEquals(result, ':f PRIVMSG t :line1')

    def test_build_privmsg_in_with_newline(self):
        result = weechat_otr.build_privmsg_in('f', 't', 'line1\nline2')
        self.assertEquals(result, ':f PRIVMSG t :line1\n:f PRIVMSG t :line2')

    def test_command_cb_start_send_tag_off(self):
        weechat_otr.command_cb(None, None, 'start')
        printed = sys.modules['weechat'].printed['buffer']

        self.assertEquals(printed, [
          'otr\tSending OTR query... Please await confirmation of the OTR ' +
          'session being started before sending a message.',

          'otr\tTo try OTR on all conversations with nick@server: /otr ' +
          'policy send_tag on'
          ])

    def test_command_cb_start_send_tag_off_no_hints(self):
        sys.modules['weechat'].config_options[
            'otr.general.hints'] = 'off'
        weechat_otr.command_cb(None, None, 'start')

        self.assertEquals(False, 'buffer' in sys.modules['weechat'].printed)

    def test_command_cb_start_send_tag_on(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.nick.send_tag'] = 'on'
        weechat_otr.command_cb(None, None, 'start')
        printed = sys.modules['weechat'].printed['buffer']

        self.assertEquals(printed, [
          'otr\tSending OTR query... Please await confirmation of the OTR ' +
          'session being started before sending a message.',
          ])

    def test_command_cb_start_send_tag_on_no_hints(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.nick.send_tag'] = 'on'
        sys.modules['weechat'].config_options[
            'otr.general.hints'] = 'off'
        weechat_otr.command_cb(None, None, 'start')

        self.assertEquals(False, 'buffer' in sys.modules['weechat'].printed)
