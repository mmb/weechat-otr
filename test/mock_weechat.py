import sys
import types

class MockWeechat(types.ModuleType):

    def __init__(self):
        pass

    def bar_item_new(*args):
        pass

    def bar_item_update(*args):
        pass

    def config_boolean(*args):
        pass

    def config_get(*args):
        pass

    def config_new(*args):
        pass

    def config_new_option(*args):
        pass

    def config_new_section(*args):
        pass

    def config_read(*args):
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
        results = {
            'irc_nick': 'nick',
            'weechat_dir': '/tmp/weechat'
        }

        return results.get(name)

    def mkdir_home(self, *args):
        pass

    def prnt(*args):
        pass

    def register(self, *args):
        return True

sys.modules['weechat'] = MockWeechat()
