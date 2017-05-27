# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import os.path
import sys

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
            ' !:)\t'
            '(color default)nick2@server2 |{fp2}\r\n'
            '(color default)nick@server   |{fp1}').format(
                fp1=account1.getPrivkey(),
                fp2=account2.getPrivkey()))

    def test_fingerprint_pattern(self):
        fpr_path1 = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'nick@server.fpr')
        with open(fpr_path1, 'w') as f:
            for fields in [
                    ['notamachxxx@server', 'nick@server', 'irc', 'fp123', ''],
                    ['matchxxxxxx@server', 'nick@server', 'irc', 'fp123', ''],
                    ['beforematch@server', 'nick@server', 'irc', 'fp123', ''],
                    ['before@servermatch', 'nick@server', 'irc', 'fp123', ''],
                ]:
                f.write("\t".join(fields))
                f.write("\n")

        account1 = weechat_otr.ACCOUNTS['nick@server']
        account1.getPrivkey()

        weechat_otr.command_cb(None, None, 'fingerprint match')

        self.assertNoPrintedContains('', 'notamachxxx@server')

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t'
            '(color default)before@servermatch |nick@server |F P 1 2 3 |'
            'unverified\r\n'
            '(color default)beforematch@server |nick@server |F P 1 2 3 |'
            'unverified\r\n'
            '(color default)matchxxxxxx@server |nick@server |F P 1 2 3 |'
            'unverified'))

    def test_fingerprint_all(self):
        fpr_path1 = os.path.join(
            sys.modules['weechat'].weechat_dir,
            'otr',
            'nick@server.fpr')
        with open(fpr_path1, 'w') as f:
            for fields in [
                    ['peer1@server', 'nick@server', 'irc', 'fp111', ''],
                    ['peer2@server', 'nick@server', 'irc', 'fp222', 'smp'],
                    ['peer3@server', 'nick@server', 'irc', 'fp333', 'verified'],
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
                    ['peer4@server2', 'nick2@server2', 'irc', 'fp444',
                     'verified'],
                ]:
                f.write("\t".join(fields))
                f.write("\n")

        account2 = weechat_otr.ACCOUNTS['nick2@server2']
        account2.getPrivkey()

        weechat_otr.command_cb(None, None, 'fingerprint all')

        self.assertPrinted('', (
            'eval(${color:default}:! ${color:brown}otr${color:default}'
            ' !:)\t'
            '(color default)peer4@server2 |nick2@server2 |F P 4 4 4 |'
            'verified    \r\n'
            '(color default)peer1@server  |nick@server   |F P 1 1 1 |'
            'unverified  \r\n'
            '(color default)peer2@server  |nick@server   |F P 2 2 2 |'
            'SMP verified\r\n'
            '(color default)peer3@server  |nick@server   |F P 3 3 3 |'
            'verified    '))
