from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class HtmlEscapePolicyTestCase(WeechatOtrTestCase):

    def test_default_html_escape_policy(self):
        result = weechat_otr.message_out_cb(None, None, b'server',
            b':nick!user@host PRIVMSG friend :< > " \' &')
        self.assertEqual(result, b'PRIVMSG friend :< > " \' &')

    def test_html_escape_policy(self):
        sys.modules['weechat'].config_options[
            'otr.policy.server.nick.friend.html_escape'] = 'on'

        result = weechat_otr.message_out_cb(None, None, b'server',
            b':nick!user@host PRIVMSG friend :< > " \' &')
        self.assertEqual(result, b'PRIVMSG friend :&lt; &gt; " \' &amp;')
