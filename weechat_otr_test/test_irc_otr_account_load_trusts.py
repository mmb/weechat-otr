# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

import os.path
import sys

class IrcOtrAccountLoadTrustsTestCase(WeechatOtrTestCase):

    def test_trust_non_ascii(self):
        fpr_path = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'nick@server.fpr')
        with open(fpr_path, 'w') as f:
            f.write(weechat_otr.PYVER.to_str(
                "gefährte@server\tnick@server\tirc\tfp123\tverified\n"))

        account1 = weechat_otr.ACCOUNTS['nick@server']
        self.assertEqual('verified', 
            account1.getTrust('gefährte@server', 'fp123'))
