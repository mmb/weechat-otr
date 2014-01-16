from __future__ import unicode_literals

import sys
import unittest

import weechat_otr_test.mock_weechat
sys.modules['weechat'] = weechat_otr_test.mock_weechat.MockWeechat()

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
