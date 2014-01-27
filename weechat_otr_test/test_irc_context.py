# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class IrcContextTestCase(WeechatOtrTestCase):

    def test_repr(self):
        self.assertRegexpMatches(
            weechat_otr.IrcContext(None, 'nick@server').__repr__(),
            r'<IrcContext [\da-f]+ peer_nick=nick peer_server=server>')
