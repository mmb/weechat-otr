# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr_test.mock_account

import weechat_otr

class ContextGetLoggerOptionNameTestCase(WeechatOtrTestCase):

    def test_get_log_level(self):
        account = weechat_otr_test.mock_account.MockAccount()
        context = weechat_otr.IrcContext(account, 'nick@server')

        self.assertEqual(
            context.get_logger_option_name(),
            'logger.level.irc.server_nick_buffer_name')
