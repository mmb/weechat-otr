# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class IrcHTMLParserTestCase(WeechatOtrTestCase):

    def after_setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.parser = weechat_otr.IrcHTMLParser()

    def test_tag_a(self):
        self.check_parse_result(
            'this is a <a href="http://weechat.org">link</a>',
            'this is a [link](http://weechat.org)'
            )

    def test_tag_a_non_ascii(self):
        self.check_parse_result(
            'this is a <a href="http://weechat.org">verknüpfung</a>',
            'this is a [verknüpfung](http://weechat.org)'
            )

    def test_tag_a_same(self):
        self.check_parse_result(
            '<a href="http://weechat.org">http://weechat.org</a>',
            '[http://weechat.org]'
            )

    def test_tag_br(self):
        self.check_parse_result(
            'foo<br>bar<br/>baz',
            'foo\nbar\nbaz'
            )

    def test_tag_unknown(self):
        self.check_parse_result(
            '<font style="awesome"><blink>none of ' \
            '<marquee behavior="alternate">this</marquee></blink> ' \
            'matters</font>',
            'none of this matters'
            )

    def test_entity_named(self):
        self.check_parse_result(
            'tom &amp; jerry',
            'tom & jerry'
            )

    def test_entity_numeric(self):
        self.check_parse_result(
            '&#60;html&#x003E;',
            '<html>'
            )

    def check_parse_result(self, html, result):
        self.parser.feed(html)
        self.parser.close()

        self.assertEqual(self.parser.result, result)
        self.assertEqual(
            self.parser.result, weechat_otr.IrcHTMLParser.parse(html))
