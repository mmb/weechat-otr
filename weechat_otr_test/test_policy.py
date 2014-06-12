# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class TestPolicy(WeechatOtrTestCase):

    def test_policy_default_server_nick_buffer(self):
        weechat_otr.command_cb(None, None, 'policy default')

        self.assertPrinted('server_nick_buffer', (
            'eval(${color:default}- ${color:brown}otr${color:default} -)\t'
            '(color default)'
            'Current default OTR policies:\r\n'
            '(color default)'
            '  allow_v2 (allow OTR protocol version 2) : on\r\n'
            '(color default)'
            '  html_escape (escape HTML special characters in outbound '
            'messages) : off\r\n'
            '(color default)'
            '  html_filter (filter HTML in incoming messages) : on\r\n'
            '(color default)'
            '  log (enable logging of OTR conversations) : off\r\n'
            '(color default)'
            '  require_encryption (refuse to send unencrypted messages) : '
            'off\r\n'
            '(color default)'
            '  send_tag (advertise your OTR capability using the whitespace '
            'tag) : off\r\n'
            '(color default)'
            'Change default policies with: /otr policy default NAME on|off'))

    def test_policy_default_no_server_nick_buffer(self):
        weechat_otr.command_cb(None, 'non_private_buffer', 'policy default')

        self.assertPrinted('', (
            'Current default OTR policies:\n'
            '  allow_v2 (allow OTR protocol version 2) : on\n'
            '  html_escape (escape HTML special characters in outbound '
            'messages) : off\n'
            '  html_filter (filter HTML in incoming messages) : on\n'
            '  log (enable logging of OTR conversations) : off\n'
            '  require_encryption (refuse to send unencrypted messages) : '
            'off\n'
            '  send_tag (advertise your OTR capability using the whitespace '
            'tag) : off\n'
            'Change default policies with: /otr policy default NAME on|off'))
