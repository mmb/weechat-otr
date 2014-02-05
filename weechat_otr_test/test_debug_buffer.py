# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

import sys

class ShutdownTestCase(WeechatOtrTestCase):

    def xtest_debug_option_off(self):
        sys.modules['weechat'].config_options['otr.general.debug'] = 'off'
        weechat_otr.debug('test')

        self.assertNotPrinted('OTR Debug', 'otr debug\ttest')

    def xtest_debug_buffer_on(self):
        sys.modules['weechat'].config_options['otr.general.debug'] = 'on'
        weechat_otr.debug('test')

        self.assertPrinted('OTR Debug', 'otr debug\ttest')

    def xtest_debug_buffer_non_ascii(self):
        sys.modules['weechat'].config_options['otr.general.debug'] = 'on'
        weechat_otr.debug('gefährte')

        self.assertPrinted('OTR Debug',
            weechat_otr.PYVER.to_str('otr debug\tgefährte'))

    def test_creates_buffer(self):
        sys.modules['weechat'].config_options['otr.general.debug'] = 'on'
        weechat_otr.debug('test')

        self.assertEqual(sys.modules['weechat'].buffer_new_buffers, {
            'OTR Debug' : {
                'input_cb' : '',
                'input_cb_args' : '',
                'close_cb' : 'debug_buffer_close_cb',
                'close_cb_args' : '',
                'buf_sets' : {
                    'title' : 'OTR Debug',
                    'localvar_set_no_log' : '1',
                    }
                }
            })

    def test_caches_buffer(self):
        sys.modules['weechat'].config_options['otr.general.debug'] = 'on'
        weechat_otr.debug('test1')
        weechat_otr.debug('test2')

        self.assertEqual(1, len(sys.modules['weechat'].buffer_new_calls))

    def test_close_callback(self):
        result = weechat_otr.debug_buffer_close_cb(None, None)
        self.assertEqual(sys.modules['weechat'].WEECHAT_RC_OK, result)
        self.assertIsNone(weechat_otr.otr_debug_buffer)
