# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

import os.path
import sys

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

    def test_fingerprint_pattern(self):
        fpr_path1 = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'nick@server.fpr')
        with open(fpr_path1, 'w') as f:
            for fields in [
                ['notamachxxx@server', 'nick@server', 'irc', 'fp', ''],
                ['matchxxxxxx@server', 'nick@server', 'irc', 'fp', ''],
                ['beforematch@server', 'nick@server', 'irc', 'fp', ''],
                ['before@servermatch', 'nick@server', 'irc', 'fp', ''],
                ]:
                f.write("\t".join(fields))
                f.write("\n")

        account1 = weechat_otr.ACCOUNTS['nick@server']
        account1.getPrivkey()

        weechat_otr.command_cb(None, None, 'fingerprint match')

        self.assertNoPrintedContains('', 'notamachxxx@server')

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t(color default)matchxxxxxx@server (nick@server) fingerprint '
            'fp unverified'))

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t(color default)beforematch@server (nick@server) fingerprint '
            'fp unverified'))

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t(color default)before@servermatch (nick@server) fingerprint '
            'fp unverified'))

    def test_fingerprint_all(self):
        fpr_path1 = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'nick@server.fpr')
        with open(fpr_path1, 'w') as f:
            for fields in [
                ['peer1@server', 'nick@server', 'irc', 'fp1', ''],
                ['peer2@server', 'nick@server', 'irc', 'fp2', 'smp'],
                ['peer3@server', 'nick@server', 'irc', 'fp3', 'verified'],
                ]:
                f.write("\t".join(fields))
                f.write("\n")

        account1 = weechat_otr.ACCOUNTS['nick@server']
        account1.getPrivkey()

        fpr_path2 = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'nick2@server2.fpr')
        with open(fpr_path2, 'w') as f:
            for fields in [
                ['peer4@server2', 'nick2@server2', 'irc', 'fp4', 'verified'],
                ]:
                f.write("\t".join(fields))
                f.write("\n")

        account2 = weechat_otr.ACCOUNTS['nick2@server2']
        account2.getPrivkey()

        weechat_otr.command_cb(None, None, 'fingerprint all')

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t(color default)peer1@server (nick@server) fingerprint '
            'fp1 unverified'))

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t(color default)peer2@server (nick@server) fingerprint '
            'fp2 SMP verified'))

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t(color default)peer3@server (nick@server) fingerprint '
            'fp3 verified'))

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t(color default)peer4@server2 (nick2@server2) fingerprint '
            'fp4 verified'))
