# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

import weechat_otr_test.recording_context

import weechat_otr

class RecordingAccount(weechat_otr.IrcOtrAccount):

    contextclass = weechat_otr_test.recording_context.RecordingContext

    def __init__(self, name):
        super(RecordingAccount, self).__init__(name)
