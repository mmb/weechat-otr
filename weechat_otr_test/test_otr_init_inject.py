# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr_test.recording_account
import weechat_otr

class OtrInitInjectTestCase(WeechatOtrTestCase):

    def test_inject_initial_otr_message(self):
        account = weechat_otr_test.recording_account.RecordingAccount(
            'nick@server')
        weechat_otr.ACCOUNTS['nick@server'] = account

        weechat_otr.message_in_cb(None, None, 'server',
            ':peer!user@host PRIVMSG nick :?OTRv2?')

        context = account.getContext('peer@server')

        self.assertTrue(context.injected[0].startswith(b'?OTR:'))
