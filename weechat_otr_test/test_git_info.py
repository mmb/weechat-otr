# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

import os
import shutil
import subprocess
import tempfile

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

class TestGitInfo(WeechatOtrTestCase):

    def after_setup(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test')
        open(self.test_file, 'w').close()

        self.prev_file = weechat_otr.__file__
        weechat_otr.__file__ = self.test_file

    def after_teardown(self):
        shutil.rmtree(self.temp_dir)
        weechat_otr.__file__ = self.prev_file

    def test_git_info(self):
        try:
            process = subprocess.Popen(['git', 'init', '--quiet', self.temp_dir])
        except OSError:
            self.skipTest('install git to run this test')
        process.communicate()

        git_dir = os.path.join(self.temp_dir, '.git')
        process = subprocess.Popen([
            'git',
            '--git-dir', git_dir,
            '--work-tree', self.temp_dir,
            'add', '.'])
        process.communicate()

        process = subprocess.Popen([
            'git',
            '--git-dir', git_dir,
            '--work-tree', self.temp_dir,
            'config',
            'user.email', 'testy@test.com'])
        process.communicate()

        process = subprocess.Popen([
            'git',
            '--git-dir', git_dir,
            '--work-tree', self.temp_dir,
            'config',
            'user.name', 'test'])
        process.communicate()

        process = subprocess.Popen([
            'git',
            '--git-dir', git_dir,
            '--work-tree', self.temp_dir,
            'commit',
            '--quiet',
            '-m',
            'test'])
        process.communicate()

        self.assertRegex(weechat_otr.git_info(), '[0-9a-f]+')

    def test_git_info_failure(self):
        self.assertEqual(weechat_otr.git_info(), None)
