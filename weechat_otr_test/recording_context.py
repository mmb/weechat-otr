# pylint: disable=missing-docstring

import weechat_otr

class RecordingContext(weechat_otr.IrcContext):

    def __init__(self, account, peername):
        super(RecordingContext, self).__init__(account, peername)

        self.injected = []

    def inject(self, msg, appdata=None):
        self.injected.append(msg)

        super(RecordingContext, self).inject(msg, appdata)
