# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

import sys

class WeechatVersionOkTestCase(WeechatOtrTestCase):

    def test_empty_version(self):
        sys.modules['weechat'].infos[('',)]['version_number'] = ''
        sys.modules['weechat'].infos[('',)]['version'] = ''
        self.assertFalse(weechat_otr.weechat_version_ok())
        self.assertPrinted('',
            'otr requires WeeChat version >= 0.4.0. The current version is '
            '.')

    def test_too_low(self):
        sys.modules['weechat'].infos[('',)]['version_number'] = 0x00030800
        sys.modules['weechat'].infos[('',)]['version'] = '0.3.8'
        self.assertFalse(weechat_otr.weechat_version_ok())
        self.assertPrinted('',
            'otr requires WeeChat version >= 0.4.0. The current version is '
            '0.3.8.')

    def test_ok(self):
        sys.modules['weechat'].infos[('',)]['version_number'] = 0x01000100
        sys.modules['weechat'].infos[('',)]['version'] = '1.0.1'
        self.assertTrue(weechat_otr.weechat_version_ok())
        self.assertNotPrinted('',
            'otr requires WeeChat version >= 0.4.0. The current version is '
            '1.0.1.')

    def test_version_checked_during_setup(self):
        self.assertIn(
            ('version_number', ('',)), sys.modules['weechat'].info_gets)
