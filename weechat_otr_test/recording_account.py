# -*- coding: utf-8 -*-
# pylint: disable=abstract-method
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

import weechat_otr_test.recording_context

import weechat_otr

class RecordingAccount(weechat_otr.IrcOtrAccount):
    contextclass = weechat_otr_test.recording_context.RecordingContext
