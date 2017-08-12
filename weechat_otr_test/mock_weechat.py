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

import collections
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
                'version_number': 0x01000100,
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
            ('server,STATUSMSG',) : {
                'irc_server_isupport_value' : '@+',
                },
            ('server,CHANTYPES',) : {
                'irc_server_isupport_value' : '#',
                },
        }
        self.buffers = {
            None : {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick',
                'localvar_server' : 'server',
                'localvar_nick' : 'me',
                },
            'server_nick_buffer' : {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick',
                'localvar_server' : 'server',
                'name' : 'server_nick_buffer_name',
                'plugin' : 'irc',
                },
            'server_nick2_buffer': {
                'localvar_type' : 'private',
                'localvar_channel' : 'nick2',
                'localvar_server' : 'server',
                'name' : 'server_nick2_buffer_name',
                'plugin' : 'irc',
                },
            'non_private_buffer' : {
                'localvar_type' : 'non_private',
                'name' : 'non_private_buffer_name',
                'plugin' : 'irc',
                }
            }
        self.config_written = []
        self.bar_items_removed = []
        self.config_section_free_options_calls = []
        self.config_section_free_calls = []
        self.config_free_calls = []
        self.buffer_new_calls = []
        self.buffer_sets = {}
        self.buffer_search_calls = []
        self.buffer_search_returns = []
        self.info_hashtables = {}
        self.info_get_hashtable_raise = None
        self.infolists = {}
        self.config_integer_defaults = {}
        self.commands = []
        self.hook_signals = []
        self.info_gets = []
        self.window_get_pointers = {}

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
        # Note that we cannot use "with tarfile.open" due to lack of support
        # for context manager in Python 2.6
        tar = tarfile.open(fileobj=tar_io, mode='w')
        tar.add(self.weechat_dir, '.')
        tar.close()
        self.weechat_dir_tar = tar_io.getvalue()

    def restore_weechat_dir(self):
        shutil.rmtree(self.weechat_dir)
        tar_io = io.BytesIO(self.weechat_dir_tar)
        # Note that we cannot use "with tarfile.open" due to lack of support
        # for context manager in Python 2.6
        tar = tarfile.open(fileobj=tar_io)
        tar.extractall(self.weechat_dir)
        tar.close()

    def bar_item_new(*args):
        return 'bar item'

    def bar_item_update(*args):
        pass

    def buffer_get_string(self, buf, string):
        return self.buffers[buf].get(string)

    def buffer_search(self, plugin, name):
        self.buffer_search_calls.append((plugin, name))
        return self.buffer_search_returns.pop(0)

    def command(self, *args):
        self.commands.append(args)

    def config_boolean(self, val):
        if val == 'on':
            return 1
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

    def config_string(self, key):
        return key

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

    def hook_signal(self, *args):
        self.hook_signals.append(args)

    def info_get(self, name, *args):
        self.info_gets.append((name, args))

        return self.infos[args].get(name)

    def info_get_hashtable(self, name, args):
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-nested-blocks
        if self.info_get_hashtable_raise:
            # pylint: disable=raising-bad-type
            raise self.info_get_hashtable_raise
        if name in self.info_hashtables:
            return self.info_hashtables[name].pop()
        if name == 'irc_message_parse':
            # Python translation of WeeChat's message parsing code.
            #
            # https://github.com/weechat/weechat/blob/bd06f0f60f8c3f5ab883df9c
            # b876fe29715055b3/src/plugins/irc/irc-message.c#L43-210
            result = {
                'arguments' : '',
                'channel' : '',
                'host' : '',
                'nick' : ''
                }

            nick_set = False

            ptr_message = args['message']

            if ptr_message[0] == ':':
                pos3 = ptr_message.find('@')
                pos2 = ptr_message.find('!')
                pos = ptr_message.find(' ')
                if pos2 == -1 or (pos != -1 and pos2 > pos):
                    pos2 = pos3
                if pos2 != -1 and (pos == -1 or pos > pos2):
                    result['nick'] = ptr_message[1:pos2]
                    nick_set = True
                elif pos != -1:
                    result['nick'] = ptr_message[1:pos]
                    nick_set = True
                if pos != -1:
                    result['host'] = ptr_message[1:pos]
                    ptr_message = ptr_message[pos:].lstrip()
                else:
                    result['host'] = ptr_message[1:]
                    ptr_message = ''

            if ptr_message:
                pos = ptr_message.find(' ')
                if pos != -1:
                    result['command'] = ptr_message[:pos]
                    pos += 1
                    while ptr_message[pos] == ' ':
                        pos += 1
                    result['arguments'] = ptr_message[pos:]
                    if ptr_message[pos] != ':':
                        if ptr_message[pos] in ('#', '&', '+', '!'):
                            pos2 = ptr_message[pos:].find(' ')
                            if pos2 != -1:
                                result['channel'] = ptr_message[pos:][:pos2]
                            else:
                                result['channel'] = ptr_message[pos:]
                        else:
                            pos2 = ptr_message[pos:].find(' ')
                            if not nick_set:
                                if pos2 != -1:
                                    result['nick'] = ptr_message[pos:][:pos2]
                                else:
                                    result['nick'] = ptr_message[pos:]
                            if pos2 != -1:
                                pos3 = pos2
                                pos2 += 1
                                while ptr_message[pos2] == ' ':
                                    pos2 += 1
                                if ptr_message[pos2] in ('#', '&', '+', '!'):
                                    pos4 = ptr_message[pos2:].find(' ')
                                    if pos4 != -1:
                                        result['channel'] = \
                                            ptr_message[pos2:][:pos4]
                                    else:
                                        result['channel'] = ptr_message[pos2:]
                                elif not result['channel']:
                                    result['channel'] = ptr_message[pos:][:pos3]
                else:
                    result['command'] = ptr_message

            return result

    def infolist_free(*args):
        pass

    def infolist_get(self, *args):
        return collections.deque(self.infolists.get(args, []) + [False])

    def infolist_next(self, infolist):
        # The current item in the infolist is the last item.
        infolist.rotate(-1)
        return infolist[-1]

    def infolist_integer(self, infolist, key):
        return infolist[-1]['integer'][key]

    def infolist_pointer(self, infolist, key):
        return infolist[-1]['pointer'][key]

    def mkdir_home(self, name, mode):
        os.mkdir(os.path.join(self.weechat_dir, name), mode)

    def string_eval_expression(self, expr, pointers, extra_vars, options):
        return 'eval({0})'.format(expr)

    def config_color(self, key):
        return key

    def color(self, name):
        return '(color {0})'.format(name)

    def prnt(self, buf, message):
        self.printed.setdefault(buf, []).append(message)

    def register(self, script_name, *args):
        self.script_name = script_name

        return True

    def set_server_current_nick(self, server, nick):
        self.infos[(server, )]['irc_nick'] = nick

    def config_integer_default(self, key):
        return self.config_integer_defaults.get(key)

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

    def buffer_new(self, *args):
        self.buffer_new_calls.append(args)

        return args[0]

    def buffer_set(self, name, key, value):
        self.buffer_sets.setdefault(name, {}).update({key: value})

    def window_get_pointer(self, *args):
        return self.window_get_pointers[args]

    def add_channel_prefix(self, prefix):
        self.infos[('server,CHANTYPES',)]['irc_server_isupport_value'] += \
                prefix

    def server_no_chantypes(self):
        self.infos[('server,CHANTYPES',)]['irc_server_isupport_value'] = ''
        self.infos[('server,STATUSMSG',)]['irc_server_isupport_value'] = ''
