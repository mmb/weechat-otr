# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

from __future__ import unicode_literals

import sys

import potr

from weechat_otr_test.weechat_otr_test_case import WeechatOtrTestCase

import weechat_otr

def create_arg_test_method(command, num_args):
    def f(_):
        sys.modules['weechat'].infos.update({
            ('arg2',) : {'irc_nick' : ''},
            ('arg2,arg1',) : {'irc_buffer' : 'arg2_arg1_buffer'},
        })
        sys.modules['weechat'].buffers.update({
            'arg2_arg1_buffer' : {
                'localvar_type' : 'private',
                'name' : 'arg2_arg1_buffer_name',
                'plugin' : 'irc',
            },
        })

        args = ["arg{i}".format(i=i) for i in range(1, num_args + 1)]
        arg_str = ' '.join(args)
        try:
            weechat_otr.command_cb(
                None, None,
                "{command} {args}".format(command=command, args=arg_str))
        except potr.context.NotEncryptedError:
            pass

    return f

def add_arg_test_methods():
    commands = [
        'distrust',
        'end',
        'fingerprint',
        'fingerprinti all',
        'finish',
        'log start',
        'log stop',
        'log',
        'policy allow_v2',
        'policy default allow_v2',
        'policy default',
        'policy',
        'refresh',
        'smp abort',
        'smp ask',
        'smp respond',
        'smp',
        'start',
        'status',
        'trust',
        ]

    for command, num_args in [(c, i) for c in commands for i in range(8)]:
        method = create_arg_test_method(command, num_args)
        command_method = command.replace(' ', '_')
        setattr(ArgParsingTestCase, 'test_{command}_{num_args}_args'.format(
            command=command_method, num_args=num_args), method)

class ArgParsingTestCase(WeechatOtrTestCase):
    """Fuzz test all commands with 0 - 7 arguments.

    Find inputs that don't parse correctly and cause tracebacks.
    """
    pass

add_arg_test_methods()
