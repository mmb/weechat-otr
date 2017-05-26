# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import sys

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr_test.mock_window

import weechat_otr

class OtrStatusbarCbTestCase(WeechatOtrTestCase):

    def test_no_window_unencrypted(self):
        self.assertEqual(
            weechat_otr.otr_statusbar_cb(None, None, None),
            '(color default)OTR:(color lightred)!SEC(color default)')

    def test_window_unencrypted(self):
        window = weechat_otr_test.mock_window.MockWindow()
        sys.modules['weechat'].window_get_pointers[(window, 'buffer')] = None

        self.assertEqual(
            weechat_otr.otr_statusbar_cb(None, None, window),
            '(color default)OTR:(color lightred)!SEC(color default)')

    def test_buffer_not_private(self):
        window = weechat_otr_test.mock_window.MockWindow()
        sys.modules['weechat'].window_get_pointers[(window, 'buffer')] = \
                'non_private_buffer'

        self.assertEqual(weechat_otr.otr_statusbar_cb(None, None, window), '')

    def test_encrypted_authenticated_logged(self):
        context = self.setup_context('me@server', 'nick@server')
        context.encrypted = True
        context.verified = True
        context.logged = True

        self.assertEqual(
            weechat_otr.otr_statusbar_cb(None, None, None),
            '(color default)OTR:(color green)SEC(color default),(color green)'
            'AUTH(color default),(color lightred)LOG(color default)')

    def test_encrypted_authenticated_not_logged(self):
        context = self.setup_context('me@server', 'nick@server')
        context.encrypted = True
        context.verified = True
        context.logged = False

        self.assertEqual(
            weechat_otr.otr_statusbar_cb(None, None, None),
            '(color default)OTR:(color green)SEC(color default),(color green)'
            'AUTH(color default),(color green)!LOG(color default)')

        self.assertEqual(sys.modules['weechat'].buffer_sets, {
            None: {
                'localvar_set_otr_encrypted': 'true',
                'localvar_set_otr_authenticated': 'true',
                'localvar_set_otr_logged': 'false',
                }})

    def test_encrypted_unauthenticated_logged(self):
        context = self.setup_context('me@server', 'nick@server')
        context.encrypted = True
        context.verified = False
        context.logged = True

        self.assertEqual(
            weechat_otr.otr_statusbar_cb(None, None, None),
            '(color default)OTR:(color green)SEC(color default),'
            '(color lightred)!AUTH(color default),(color lightred)LOG'
            '(color default)')

        self.assertEqual(sys.modules['weechat'].buffer_sets, {
            None: {
                'localvar_set_otr_encrypted': 'true',
                'localvar_set_otr_authenticated': 'false',
                'localvar_set_otr_logged': 'true',
                }})

    def test_encrypted_unauthenticated_not_logged(self):
        context = self.setup_context('me@server', 'nick@server')
        context.encrypted = True
        context.verified = False
        context.logged = False

        self.assertEqual(
            weechat_otr.otr_statusbar_cb(None, None, None),
            '(color default)OTR:(color green)SEC(color default),'
            '(color lightred)!AUTH(color default),(color green)!LOG'
            '(color default)')

        self.assertEqual(sys.modules['weechat'].buffer_sets, {
            None: {
                'localvar_set_otr_encrypted': 'true',
                'localvar_set_otr_authenticated': 'false',
                'localvar_set_otr_logged': 'false',
                }})

    def test_unencrypted_unauthenticated_logged(self):
        context = self.setup_context('me@server', 'nick@server')
        context.encrypted = False
        context.verified = False
        context.logged = True

        self.assertEqual(
            weechat_otr.otr_statusbar_cb(None, None, None),
            '(color default)OTR:(color lightred)!SEC(color default)')

        self.assertEqual(sys.modules['weechat'].buffer_sets, {
            None: {
                'localvar_set_otr_encrypted': 'false',
                'localvar_set_otr_authenticated': 'false',
                'localvar_set_otr_logged': 'true',
                }})

    def test_unencrypted_unauthenticated_not_logged(self):
        context = self.setup_context('me@server', 'nick@server')
        context.encrypted = False
        context.verified = False
        context.logged = False

        self.assertEqual(
            weechat_otr.otr_statusbar_cb(None, None, None),
            '(color default)OTR:(color lightred)!SEC(color default)')

        self.assertEqual(sys.modules['weechat'].buffer_sets, {
            None: {
                'localvar_set_otr_encrypted': 'false',
                'localvar_set_otr_authenticated': 'false',
                'localvar_set_otr_logged': 'false',
                }})
