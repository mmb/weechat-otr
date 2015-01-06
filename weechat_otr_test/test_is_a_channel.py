# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class IsAChannelTestCase(WeechatOtrTestCase):

    def test_hash(self):
        self.assertTrue(weechat_otr.is_a_channel('#channel'))

    def test_ampersand(self):
        self.assertTrue(weechat_otr.is_a_channel('&channel'))

    def test_plus(self):
        self.assertTrue(weechat_otr.is_a_channel('+channel'))

    def test_bang(self):
        self.assertTrue(weechat_otr.is_a_channel('!channel'))

    def test_at(self):
        self.assertTrue(weechat_otr.is_a_channel('@#channel'))

    def test_not_a_channel(self):
        self.assertFalse(weechat_otr.is_a_channel('nick'))
