import unittest

import mock_weechat

import weechat_otr

class WeechatOtrTestCase(unittest.TestCase):

    def test_message_out_cb(self):
        result = weechat_otr.message_out_cb(None, None, 'freenode',
            ':nick!user@host PRIVMSG friend :hello')
        self.assertEquals(result, 'PRIVMSG friend :hello')
