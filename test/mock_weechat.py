import copy
import types

class MockWeechat(types.ModuleType):

    WEECHAT_RC_ERROR = None
    WEECHAT_RC_OK = None

    def __init__(self):
        self.config_options = {}
        self.script_name = None
        self.printed = {}

    def save(self):
        self.saved_state = copy.deepcopy(self.__dict__)

    def restore(self):
        prev_state = copy.deepcopy(self.saved_state)
        self.__dict__.clear()
        self.__dict__.update(prev_state)

    def bar_item_new(*args):
        pass

    def bar_item_update(*args):
        pass

    def buffer_get_string(self, buf, string):
        strings = {
            'localvar_type' : 'private',
            'localvar_channel' : 'nick',
            'localvar_server' : 'server',
            }

        return strings.get(string)

    def command(*args):
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
        infos = {
            'irc_buffer' : 'buffer',
            'irc_nick': 'nick',
            'weechat_dir': '/tmp/weechat'
        }

        return infos.get(name)

    def infolist_free(*args):
        pass

    def infolist_get(*args):
        pass

    def infolist_next(*args):
        pass

    def mkdir_home(self, *args):
        pass

    def prnt(self, buf, message):
        self.printed.setdefault(buf, []).append(message)

    def register(self, script_name, *args):
        self.script_name = script_name

        return True

