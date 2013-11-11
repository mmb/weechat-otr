import types

class MockWeechat(types.ModuleType):

    def __init__(self):
        self.config_options = {}
        self.script_name = None

    def bar_item_new(*args):
        pass

    def bar_item_update(*args):
        pass

    def config_boolean(self, s):
        if s == 'on':
            return 1
        else:
            return 0

    def config_get(self, key):
        return self.config_options.get(key, '')

    def config_new(*args):
        pass

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
        infos = {
            'irc_nick': 'nick',
            'weechat_dir': '/tmp/weechat'
        }

        return infos.get(name)

    def mkdir_home(self, *args):
        pass

    def prnt(*args):
        pass

    def register(self, script_name, *args):
        self.script_name = script_name

        return True

