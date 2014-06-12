# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr_test.mock_account

import weechat_otr

class ContextTestCase(WeechatOtrTestCase):

    def test_print_buffer(self):
        account = weechat_otr_test.mock_account.MockAccount()
        context = weechat_otr.IrcContext(account, 'nick@server')
        context.print_buffer('a message from the script')

        self.assertPrinted('server_nick_buffer',
            'eval(${color:default}- ${color:brown}otr${color:default} -)\t'
            'a message from the script')

    def test_print_buffer_non_ascii(self):
        account = weechat_otr_test.mock_account.MockAccount()
        context = weechat_otr.IrcContext(account, 'nick@server')
        context.print_buffer('gefährte')

        self.assertPrinted('server_nick_buffer',
            weechat_otr.PYVER.to_str(
              'eval(${color:default}- ${color:brown}otr${color:default} -)\t'
              'gefährte'))
