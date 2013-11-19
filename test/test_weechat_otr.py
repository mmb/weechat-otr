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
