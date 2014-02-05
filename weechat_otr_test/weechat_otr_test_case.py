# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name

from __future__ import unicode_literals

import sys
import tempfile
import unittest

import weechat_otr_test.mock_weechat
sys.modules['weechat'] = weechat_otr_test.mock_weechat.MockWeechat(
    tempfile.mkdtemp())

import weechat_otr

class WeechatOtrTestCase(unittest.TestCase):

    def setUp(self):
        sys.modules['weechat'].save()
        weechat_otr.ACCOUNTS.clear()
        weechat_otr.otr_debug_buffer = None
        self.after_setup()

    def tearDown(self):
        sys.modules['weechat'].restore()
        self.after_teardown()

    def after_setup(self):
        pass

    def after_teardown(self):
        pass

    def assertPrinted(self, buf, text):
        self.assertIn(text, sys.modules['weechat'].printed[buf])

    def assertNotPrinted(self, buf, text):
        self.assertNotIn(text, sys.modules['weechat'].printed.get(buf, []))
