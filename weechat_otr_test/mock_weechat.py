# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=no-method-argument
# pylint: disable=no-self-use
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument
# pylint: disable=too-many-instance-attributes
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments

from __future__ import unicode_literals

import copy
import io
import os
import shutil
import tarfile
import types

class MockWeechat(types.ModuleType):

    WEECHAT_RC_ERROR = None
    WEECHAT_RC_OK = None

    def __init__(self, weechat_dir):
        self.weechat_dir = weechat_dir

        self.config_options = {}
        self.script_name = None
        self.printed = {}
        self.saved_state = None
        self.weechat_dir_tar = None
        self.infos = {
            ('',) : {
                'weechat_dir': self.weechat_dir,
                },
            ('server',) : {
                'irc_nick': 'nick',
                },
            ('server,nick',) : {
                'irc_buffer' : 'server_nick_buffer',
                },
            ('server,nick2',) : {
                'irc_buffer' : 'server_nick2_buffer',
                },
            ('server,no_window_nick',) : {
                'irc_buffer' : 'non_private_buffer',
                },
        }
        self.buffers = {
            None : {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick',
                'localvar_server' : 'server',
                },
            'server_nick_buffer' : {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick',
                'localvar_server' : 'server',
                },
            'server_nick2_buffer': {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick2',
                'localvar_server' : 'server',
                },
            'non_private_buffer' : {
                'localvar_type' : 'non_private',
                }
            }
        self.config_written = []
        self.bar_items_removed = []
        self.config_section_free_options_calls = []
        self.config_section_free_calls = []
        self.config_free_calls = []
        self.buffer_new_calls = []
        self.buffer_new_buffers = {}

    def save(self):
        self.snapshot_weechat_dir()
        self.saved_state = copy.deepcopy(self.__dict__)

    def restore(self):
        prev_state = copy.deepcopy(self.saved_state)
        self.__dict__.clear()
        self.__dict__.update(prev_state)

        self.restore_weechat_dir()

    def snapshot_weechat_dir(self):
        tar_io = io.BytesIO()
        with tarfile.open(fileobj=tar_io, mode='w') as tar:
            tar.add(self.weechat_dir, '.')
        self.weechat_dir_tar = tar_io.getvalue()

    def restore_weechat_dir(self):
        shutil.rmtree(self.weechat_dir)
        tar_io = io.BytesIO(self.weechat_dir_tar)
        with tarfile.open(fileobj=tar_io) as tar:
            tar.extractall(self.weechat_dir)

    def bar_item_new(*args):
        return 'bar item'

    def bar_item_update(*args):
        pass

    def buffer_get_string(self, buf, string):
        return self.buffers[buf].get(string)

    def command(*args):
        pass

    def config_boolean(self, val):
        if val == 'on':
            return 1
        else:
            return 0

    def config_get(self, key):
        return self.config_options.get(key, '')

    def config_new(*args):
        return 'config file'

    def config_new_option(self, config_file, section, name, *args):
        parts = [self.script_name]
        if section is not None:
            parts.append(section)
        parts.append(name)
        default = args[5]
        full_option_name = '.'.join(parts)

        self.config_options[full_option_name] = default

    def config_new_section(self, config_file, name, *args):
        return name

    def config_read(*args):
        pass

    def current_buffer(*args):
        pass

    def hook_command(*args):
        pass

    def hook_completion(*args):
        pass

    def hook_config(*args):
        pass

    def hook_modifier(*args):
        pass

    def hook_signal(*args):
        pass

    def info_get(self, name, *args):
        return self.infos[args].get(name)

    def infolist_free(*args):
        pass

    def infolist_get(*args):
        pass

    def infolist_next(*args):
        pass

    def mkdir_home(self, name, mode):
        os.mkdir(os.path.join(self.weechat_dir, name), mode)

    def prnt(self, buf, message):
        self.printed.setdefault(buf, []).append(message)

    def register(self, script_name, *args):
        self.script_name = script_name

        return True

    def set_server_current_nick(self, server, nick):
        self.infos[(server, )]['irc_nick'] = nick

    def config_write(self, *args):
        self.config_written.append(args)

    def config_section_free_options(self, *args):
        self.config_section_free_options_calls.append(args)

    def config_section_free(self, *args):
        self.config_section_free_calls.append(args)

    def config_free(self, *args):
        self.config_free_calls.append(args)

    def bar_item_remove(self, *args):
        self.bar_items_removed.append(args)

    def buffer_new(self, name, input_cb, input_cb_args, close_cb,
        close_cb_args):
        self.buffer_new_calls.append((name, input_cb, input_cb_args, close_cb))
        self.buffer_new_buffers[name] = dict(
            input_cb=input_cb,
            input_cb_args=input_cb_args,
            close_cb=close_cb,
            close_cb_args=close_cb_args,
            buf_sets={})

        return name

    def buffer_set(self, name, key, value):
        self.buffer_new_buffers[name]['buf_sets'][key] = value
