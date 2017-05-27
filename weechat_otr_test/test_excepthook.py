# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import io
import platform
import sys

import potr

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class TestExcepthook(WeechatOtrTestCase):

    def test_excepthook(self):
        sys.modules['weechat'].infos[('',)]['version'] = '9.8.7'

        new_stderr = io.StringIO()
        orig_stderr = sys.stderr
        sys.stderr = new_stderr
        weechat_otr.excepthook(Exception, 'error', [])
        sys.stderr = orig_stderr

        version_str = (
            'Versions: weechat-otr {script_version}, '
            'potr {potr_major}.{potr_minor}.{potr_patch}-{potr_sub}, '
            'Python {python_version}, '
            'WeeChat 9.8.7\n'
            ).format(
                script_version=weechat_otr.SCRIPT_VERSION,
                potr_major=potr.VERSION[0],
                potr_minor=potr.VERSION[1],
                potr_patch=potr.VERSION[2],
                potr_sub=potr.VERSION[3],
                python_version=platform.python_version())

        self.assertIn(version_str, new_stderr.getvalue())

    def test_excepthook_hooked(self):
        self.assertEqual(sys.excepthook, weechat_otr.excepthook)
