# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class FingerprintTestCase(WeechatOtrTestCase):

    def test_fingerprint(self):
        account1 = weechat_otr.ACCOUNTS['nick@server']
        account1.getPrivkey()

        account2 = weechat_otr.ACCOUNTS['nick2@server2']
        account2.getPrivkey()

        weechat_otr.command_cb(None, None, 'fingerprint')

        self.assertPrinted('', (
            'eval(${{color:default}}:! ${{color:brown}}otr${{color:default}}'
            ' !:)\t(color default)nick@server fingerprint '
            '{fingerprint}'.format(fingerprint=account1.getPrivkey())))

        self.assertPrinted('', (
            'eval(${{color:default}}:! ${{color:brown}}otr${{color:default}}'
            ' !:)\t(color default)nick2@server2 fingerprint '
            '{fingerprint}'.format(fingerprint=account2.getPrivkey())))

    def xtest_fingerprint_pattern(self):
        pass

    def xtest_fingerprint_all(self):
        pass
