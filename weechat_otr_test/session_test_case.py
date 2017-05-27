# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class SessionTestCase(WeechatOtrTestCase):

    def send_all(self, from_nick, to_nick, messages):
        # pylint: disable=no-self-use
        while messages:
            weechat_otr.message_in_cb(
                None, None, 'server',
                ':{from_nick}!user@host PRIVMSG {to_nick} :{message}'.format(
                    from_nick=from_nick,
                    to_nick=to_nick,
                    message=messages.pop().decode('utf-8', 'replace')))
