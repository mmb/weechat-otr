# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

import weechat_otr_test.mock_account
import weechat_otr_test.mock_context

class SmpTestCase(WeechatOtrTestCase):

    def test_smp_ask_nick_server_question_secret(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(
            None, None, 'smp ask nick2 server question secret')

        self.assertEqual(('secret', 'question'), context.smp_init)

    def test_smp_ask_nick_server_secret(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(
            None, None, 'smp ask nick2 server secret')

        self.assertEqual(('secret', None), context.smp_init)

    def test_smp_ask_question_secret(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(
            None, 'server_nick2_buffer', 'smp ask question secret')

        self.assertEqual(('secret', 'question'), context.smp_init)

    def test_smp_ask_secret(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(None, 'server_nick2_buffer', 'smp ask secret')

        self.assertEqual(('secret', None), context.smp_init)

    def test_smp_ask_nick_server_question_secret_multiple_words(self):
        context = self.setup_smp_context('nick@server', 'nick2@server')

        weechat_otr.command_cb(
            None, None, "smp ask nick2 server 'what is the secret?' "
            "'eastmost penninsula is the secret'")

        self.assertEqual(
            ('eastmost penninsula is the secret', 'what is the secret?'),
            context.smp_init)

    def setup_smp_context(self, account_name, context_name):
        # pylint: disable=no-self-use
        context = weechat_otr_test.mock_context.MockContext()
        account = weechat_otr_test.mock_account.MockAccount()
        account.add_context(context_name, context)
        weechat_otr.ACCOUNTS[account_name] = account

        return context
