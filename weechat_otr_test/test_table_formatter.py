# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr


class TableFormatterTestCase(WeechatOtrTestCase):

    def test_format(self):
        table_formatter = weechat_otr.TableFormatter()
        table_formatter.add_row(['a', 'b', 'c'])
        table_formatter.add_row(['a', 'bb', 'c'])
        table_formatter.add_row(['a', 'b', 'ccc'])

        self.assertEqual(table_formatter.format(),
            """a |b  |c  
a |bb |c  
a |b  |ccc""")
