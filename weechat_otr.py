# -*- coding: utf-8 -*-
# weechat-otr - WeeChat script for Off-the-Record messaging
#
# DISCLAIMER: To the best of my knowledge this script securely provides OTR
# messaging in WeeChat, but I offer no guarantee. Please report any security
# holes you find.
#
# Copyright (c) 2012 Matthew M. Boedicker <matthewm@boedicker.org>
#                    Nils Görs <weechatter@arcor.de>
#
# Report issues at https://github.com/mmb/weechat-otr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import collections
import os
import re

import weechat

import potr

SCRIPT_NAME = 'otr'
SCRIPT_DESC = 'Off-the-Record'
SCRIPT_AUTHOR = 'Matthew M. Boedicker'
SCRIPT_LICENCE = 'GPL3'
SCRIPT_VERSION = '0.0.2'

OTR_DIR_NAME = 'otr'

OTR_QUERY_RE = re.compile('\?OTR\??v[a-z\d]*\?$')

potr.proto.TaggedPlaintextOrig = potr.proto.TaggedPlaintext

class WeechatTaggedPlaintext(potr.proto.TaggedPlaintextOrig):
    """Patch potr.proto.TaggedPlaintext to not end plaintext tags in a space.

    When POTR adds OTR tags to plaintext it puts them at the end of the message.
    The tags end in a space which gets stripped off by WeeChat because it
    strips trailing spaces from commands. This causes OTR initiation to fail so
    the following code adds an extra tab at the end of the plaintext tags if
    they end in a space.
    """

    def __bytes__(self):
        # old style because parent class is old style
        result = potr.proto.TaggedPlaintextOrig.__bytes__(self)

        if result.endswith(' '):
            result = '%s\t' % result

        return result

potr.proto.TaggedPlaintext = WeechatTaggedPlaintext

def debug(msg):
    """Send a debug message to the WeeChat core buffer."""
    debug_option = weechat.config_get(config_prefix('general.debug'))

    if weechat.config_boolean(debug_option):
        weechat.prnt('', '%s debug\t%s' % (SCRIPT_NAME, str(msg)))

def info(msg):
    """Send an info message to the WeeChat core buffer."""
    weechat.prnt('', '%s\t%s' % (SCRIPT_NAME, str(msg)))

def current_user(server_name):
    """Get the nick and server of the current user on a server."""
    return irc_user(weechat.info_get('irc_nick', server_name), server_name)

def irc_user(nick, server):
    """Build an IRC user string from a nick and server."""
    return '%s@%s' % (nick, server)

def extract_privmsg_text(args):
    """Get the message part of PRIVMSG command arguments."""
    return args.split(' :', 1)[1]

def has_otr_end(msg):
    """Return True if the message is the end of an OTR message."""
    return msg.endswith('.') or msg.endswith(',')

def first_instance(objs, klass):
    """Return the first object in the list that is an instance of a class."""
    for obj in objs:
        if isinstance(obj, klass):
            return obj

def config_prefix(option):
    """Add the config prefix to an option and return the full option name."""
    return '%s.%s' % (SCRIPT_NAME, option)

def config_color(option):
    """Get the color of a color config option."""
    return weechat.color(weechat.config_color(weechat.config_get(
            config_prefix('color.%s' % option))))

class AccountDict(collections.defaultdict):
    """Dictionary that adds missing keys as IrcOtrAccount instances."""

    def __missing__(self, key):
        debug(('add account', key))
        self[key] = IrcOtrAccount(key)

        return self[key]

class Assembler:
    """Reassemble fragmented OTR messages.

    This does not deal with OTR fragmentation, which is handled by potr, but
    fragmentation of received OTR messages that are too large for IRC.
    """
    def __init__(self):
        self.clear()

    def add(self, data):
        """Add data to the buffer."""
        self.value += data

    def clear(self):
        """Empty the buffer."""
        self.value = ''

    def is_done(self):
        """Return True if the buffer is a complete message."""
        return self.is_query() or \
            not self.value.startswith(potr.proto.OTRTAG) or \
            has_otr_end(self.value)

    def get(self):
        """Return the current value of the buffer and empty it."""
        result = self.value
        self.clear()

        return result

    def is_query(self):
        """Return true if the buffer is an OTR query."""
        return OTR_QUERY_RE.match(self.value)

class IrcContext(potr.context.Context):
    """Context class for OTR over IRC."""

    def __init__(self, account, peername):
        super(IrcContext, self).__init__(account, peername)

        self.peer_nick, self.peer_server = peername.split('@')
        self.in_assembler = Assembler()
        self.in_otr_message = False
        self.in_smp = False
        self.smp_question = False

    def policy_config_option(self, policy):
        """Get the option name of a policy option for this context."""
        return config_prefix('.'.join([
                    'policy', self.peer_server, self.user.nick, self.peer_nick,
                    policy.lower()]))

    def getPolicy(self, key):
        """Get the value of a policy option for this context."""
        option = weechat.config_get(self.policy_config_option(key))

        if option == '':
            option = weechat.config_get(
                config_prefix('policy.default_%s' % key.lower()))

        result = bool(weechat.config_boolean(option))

        debug(('getPolicy', key, result))

        return result

    def inject(self, msg, appdata=None):
        """Send a message to the remote peer."""
        unicode_msg = unicode(msg)

        debug(('inject', unicode_msg, 'len %d' % len(unicode_msg), appdata))

        for line in unicode_msg.split("\n"):
            command = '/quote -server %s PRIVMSG %s :%s' % (
                appdata['server'], appdata['nick'], line)

            debug(command)
            weechat.command('', command)

    def setState(self, newstate):
        """Handle state transition."""
        debug(('state', self.state, newstate))

        if self.is_encrypted():
            if newstate == potr.context.STATE_ENCRYPTED:
                self.print_buffer(
                    'Private conversation has been refreshed.')
            elif newstate == potr.context.STATE_FINISHED:
                self.print_buffer(
                    """%s has ended the private conversation. You should do the same:
/otr endprivate %s %s
""" % (self.peer, self.peer_nick, self.peer_server))
        elif newstate == potr.context.STATE_ENCRYPTED:
            # unencrypted => encrypted
            trust = self.getCurrentTrust()
            if trust is None:
                fpr = str(self.getCurrentKey())
                self.print_buffer('New fingerprint: %s' % fpr)
                self.setCurrentTrust('')

            if bool(trust):
                self.print_buffer(
                    'Authenticated secured OTR conversation started.')
            else:
                self.print_buffer(
                    'Unauthenticated secured OTR conversation started.')
                self.print_buffer(self.verify_instructions())

        if self.state != potr.context.STATE_PLAINTEXT and \
                newstate == potr.context.STATE_PLAINTEXT:
            self.print_buffer('Private conversation ended.')

        super(IrcContext, self).setState(newstate)

    def buffer(self):
        """Get the buffer for this context."""
        # TODO open a new private buffer for this user if there isn't one
        return weechat.info_get(
            'irc_buffer', '%s,%s' % (self.peer_server, self.peer_nick))

    def print_buffer(self, msg):
        """Print a message to the buffer for this context."""
        weechat.prnt(self.buffer(), '%s\t%s' % (SCRIPT_NAME, msg))

    def smp_finish(self, message):
        """Reset SMP state and send a message to the user."""
        self.in_smp = False
        self.smp_question = False

        self.user.saveTrusts()
        self.print_buffer(message)

    def handle_tlvs(self, tlvs):
        """Handle SMP states."""
        if tlvs:
            smp1q = first_instance(tlvs, potr.proto.SMP1QTLV)
            smp3 = first_instance(tlvs, potr.proto.SMP3TLV)
            smp4 = first_instance(tlvs, potr.proto.SMP4TLV)

            if self.in_smp and not self.smpIsValid():
                debug('SMP aborted')
                self.smp_finish('SMP aborted.')
            elif first_instance(tlvs, potr.proto.SMP1TLV):
                debug('SMP1')
                self.in_smp = True

                self.print_buffer(
                    """Peer has requested SMP verification.
Respond with: /otr smp respond %s %s <secret>""" % (
                        self.peer_nick, self.peer_server))
            elif smp1q:
                debug(('SMP1Q', smp1q.msg))
                self.in_smp = True
                self.smp_question = True

                self.print_buffer(
                    """Peer has requested SMP verification: %s
Respond with: /otr smp respond %s %s <answer>""" % (
                        smp1q.msg, self.peer_nick, self.peer_server))
            elif first_instance(tlvs, potr.proto.SMP2TLV):
                debug('SMP2')
                self.print_buffer('SMP progressing.')
            elif smp3 or smp4:
                if smp3:
                    debug('SMP3')
                elif smp4:
                    debug('SMP4')

                if self.smpIsSuccess():
                    self.smp_finish('SMP verification succeeded.')

                    if self.smp_question:
                        self.print_buffer(
                            """You may want to authenticate your peer by asking your own question:
/otr smp ask %s %s <secret> <question>
""" % (self.peer_nick, self.peer_server))
                else:
                    self.smp_finish('SMP verification failed.')

    def verify_instructions(self):
        """Generate verification instructions for user."""
        return """You can verify that this contact is who they claim to be in one of the following ways:

1) Verify each other's fingerprints using a secure channel:
  Your fingerprint : %(your_fingerprint)s
  %(peer)s's fingerprint : %(peer_fingerprint)s
  then use the command: /otr trust %(peer_nick)s %(peer_server)s

2) SMP pre-shared secret that you both know:
  /otr smp ask %(peer_nick)s %(peer_server)s <secret>

3) SMP pre-shared secret that you both know with a question:
  /otr smp ask %(peer_nick)s %(peer_server)s <secret> <question>
""" % dict(
            your_fingerprint=self.user.getPrivkey(),
            peer=self.peer,
            peer_fingerprint=potr.human_hash(
        self.crypto.theirPubkey.cfingerprint()),
            peer_nick=self.peer_nick,
            peer_server=self.peer_server,
            )

    def is_encrypted(self):
        """Return True if the conversation with this context's peer is
        currently encrypted."""
        return self.state == potr.context.STATE_ENCRYPTED

    def is_verified(self):
        """Return True if this context's peer is verified."""
        return bool(self.getCurrentTrust())

class IrcOtrAccount(potr.context.Account):
    """Account class for OTR over IRC."""

    contextclass = IrcContext

    PROTOCOL = 'irc'
    MAX_MSG_SIZE = 417

    def __init__(self, name):
        super(IrcOtrAccount, self).__init__(
            name, IrcOtrAccount.PROTOCOL, IrcOtrAccount.MAX_MSG_SIZE)

        self.nick, self.server = self.name.split('@')

        # IRC messages cannot have newlines, OTR query and "no plugin" text
        # need to be one message
        self.defaultQuery = self.defaultQuery.replace("\n", ' ')

        self.key_file_path = os.path.join(OTR_DIR, '%s.%s' % (name, 'key3'))
        self.fpr_file_path = os.path.join(OTR_DIR, '%s.%s' % (name, 'fpr'))

        self.load_trusts()

    def load_trusts(self):
        """Load trust data from the fingerprint file."""
        if os.path.exists(self.fpr_file_path):
            with open(self.fpr_file_path) as fpr_file:
                for line in fpr_file:
                    debug(('load trust check', line))

                    context, account, protocol, fpr, trust = \
                        line[:-1].split('\t')

                    if account == self.name and \
                            protocol == IrcOtrAccount.PROTOCOL:
                        debug(('set trust', context, fpr, trust))
                        self.setTrust(context, fpr, trust)

    def loadPrivkey(self):
        """Load key file."""
        debug(('load private key', self.key_file_path))

        if os.path.exists(self.key_file_path):
            with open(self.key_file_path, 'rb') as key_file:
                return potr.crypt.PK.parsePrivateKey(key_file.read())[0]

    def savePrivkey(self):
        """Save key file."""
        debug(('save private key', self.key_file_path))

        with open(self.key_file_path, 'wb') as key_file:
            key_file.write(self.getPrivkey().serializePrivateKey())

    def saveTrusts(self):
        """Save trusts."""
        with open(self.fpr_file_path, 'w') as fpr_file:
            for uid, trusts in self.trusts.iteritems():
                for fpr, trust in trusts.iteritems():
                    debug(('trust write', uid, self.name,
                           IrcOtrAccount.PROTOCOL, fpr, trust))
                    fpr_file.write('\t'.join(
                            (uid, self.name, IrcOtrAccount.PROTOCOL, fpr,
                             trust)))
                    fpr_file.write('\n')

def message_in_cb(data, modifier, modifier_data, string):
    """Incoming message callback"""
    debug(('message_in_cb', data, modifier, modifier_data, string))

    parsed = weechat.info_get_hashtable(
        'irc_message_parse', dict(message=string))
    debug(('parsed message', parsed))

    msg_text = extract_privmsg_text(parsed['arguments'])

    server = modifier_data

    from_user = irc_user(parsed['nick'], server)
    local_user = current_user(server)

    context = ACCOUNTS[local_user].getContext(from_user)

    context.in_assembler.add(msg_text)

    result = ''

    if context.in_assembler.is_done():
        try:
            msg, tlvs = context.receiveMessage(
                context.in_assembler.get(),
                appdata=dict(nick=parsed['nick'], server=server))

            debug(('receive', msg, tlvs))

            if msg:
                result = ':%s PRIVMSG %s :%s' % (
                    parsed['host'], parsed['channel'], msg)

            context.handle_tlvs(tlvs)
        except potr.context.ErrorReceived, e:
            context.print_buffer('Received OTR error: %s' % e.args[0].error)
        except potr.context.NotEncryptedError:
            context.print_buffer(
                'Received encrypted data but no private session established.')
        except potr.context.NotOTRMessage:
            result = string
        except potr.context.UnencryptedMessage:
            result = string

    weechat.bar_item_update(SCRIPT_NAME)

    return result

def message_out_cb(data, modifier, modifier_data, string):
    """Outgoing message callback."""
    debug(('message_out_cb', data, modifier, modifier_data, string))

    parsed = weechat.info_get_hashtable(
        'irc_message_parse', dict(message=string))
    debug(('parsed message', parsed))

    # skip processing messages to public channels
    if parsed['nick'] == '':
        return string

    msg_text = extract_privmsg_text(parsed['arguments'])

    server = modifier_data

    to_user = irc_user(parsed['nick'], server)
    local_user = current_user(server)

    context = ACCOUNTS[local_user].getContext(to_user)

    result = string

    if OTR_QUERY_RE.match(msg_text):
        debug('matched OTR query')
    elif msg_text.startswith(potr.proto.OTRTAG):
        if not has_otr_end(msg_text):
            debug('in OTR message')
            context.in_otr_message = True
        else:
            debug('complete OTR message')
    elif context.in_otr_message:
        if has_otr_end(msg_text):
            context.in_otr_message = False
            debug('in OTR message end')
    else:
        debug(('context send message', msg_text, parsed['nick'], server))

        try:
            context.sendMessage(
                potr.context.FRAGMENT_SEND_ALL, msg_text,
                appdata=dict(nick=parsed['nick'], server=server))
        except potr.context.NotEncryptedError, err:
            if err.args[0] == potr.context.EXC_FINISHED:
                context.print_buffer(
                    """Your message was not sent. End your private conversation:\n/otr endprivate %s %s""" % (
                        parsed['nick'], server))
            else:
                raise

        result = ''

    weechat.bar_item_update(SCRIPT_NAME)

    return result

def shutdown():
    """Script unload callback."""
    debug('shutdown')

    weechat.config_write(CONFIG_FILE)

    free_all_config()

    weechat.bar_item_remove(OTR_STATUSBAR)

    return weechat.WEECHAT_RC_OK

def command_cb(data, buf, args):
    """Parse and dispatch WeeChat OTR commands."""
    result = weechat.WEECHAT_RC_ERROR

    arg_parts = args.split(None, 5)

    if len(arg_parts) == 3 and arg_parts[0] == 'trust':
        nick, server = arg_parts[1:3]

        context = ACCOUNTS[current_user(server)].getContext(
            irc_user(nick, server))
        context.setCurrentTrust('verified')

        result = weechat.WEECHAT_RC_OK
    elif len(arg_parts) in (5, 6) and arg_parts[0] == 'smp':
        action = arg_parts[1]

        if action == 'respond':
            nick, server, secret = arg_parts[2:5]

            context = ACCOUNTS[current_user(server)].getContext(
                irc_user(nick, server))
            context.smpGotSecret(secret, appdata=dict(nick=nick, server=server))

            result = weechat.WEECHAT_RC_OK
        elif action == 'ask':
            nick, server, secret = arg_parts[2:5]

            if len(arg_parts) > 5:
                question = arg_parts[5]
            else:
                question = None

            context = ACCOUNTS[current_user(server)].getContext(
                irc_user(nick, server))
            context.smpInit(
                secret, question, appdata=dict(nick=nick, server=server))

            result = weechat.WEECHAT_RC_OK
    elif len(arg_parts) == 3 and arg_parts[0] == 'endprivate':
        nick, server = arg_parts[1:3]

        context = ACCOUNTS[current_user(server)].getContext(
            irc_user(nick, server))
        context.disconnect(appdata=dict(nick=nick, server=server))

        result = weechat.WEECHAT_RC_OK

    return result

def otr_statusbar_cb(data, item, window):
    """Update the statusbar."""
    buf = weechat.window_get_pointer(window, 'buffer')
    buf_type = weechat.buffer_get_string(buf, 'localvar_type')

    result = ''

    if buf_type == 'private':
        local_user = irc_user(
            weechat.buffer_get_string(buf, 'localvar_nick'),
            weechat.buffer_get_string(buf, 'localvar_server'))

        remote_user = irc_user(
            weechat.buffer_get_string(buf, 'localvar_channel'),
            weechat.buffer_get_string(buf, 'localvar_server'))

        context = ACCOUNTS[local_user].getContext(remote_user)
        
        result = ''

        if context.tagOffer == potr.context.OFFER_SENT:
            result += '%sOTR?' % config_color('status.default')
        elif context.tagOffer == potr.context.OFFER_ACCEPTED:
            result += '%sOTR:' % config_color('status.default')

            if context.is_encrypted():
                result += ''.join([
                        config_color('status.encrypted'),
                        'encrypted',
                        config_color('status.default')])
                result += ','

                if context.is_verified():
                    result += ''.join([
                            config_color('status.authenticated'),
                            'authenticated',
                            config_color('status.default')])
                else:
                    result += ''.join([
                            config_color('status.unauthenticated'),
                            'unauthenticated',
                            config_color('status.default')])
            else:
                result += ''.join([
                        config_color('status.unencrypted'),
                        'unencrypted',
                        config_color('status.default')])

    return result

def policy_create_option_cb(data, config_file, section, name, value):
    """Callback for creating a new policy option when the user sets one
    that doesn't exist."""
    weechat.config_new_option(
        config_file, section, name, 'boolean', '', '', 0, 0, value, value, 0,
        '', '', '', '', '', '')

    return weechat.WEECHAT_CONFIG_OPTION_SET_OK_CHANGED

def init_config():
    """Set up configuration options and load config file."""
    global CONFIG_FILE
    CONFIG_FILE = weechat.config_new(SCRIPT_NAME, 'config_reload_cb', '')

    global CONFIG_SECTIONS
    CONFIG_SECTIONS = {}

    CONFIG_SECTIONS['general'] = weechat.config_new_section(
        CONFIG_FILE, 'general', 0, 0, '', '', '', '', '', '', '', '', '', '')

    for option, typ, desc, default in [
        ('debug', 'boolean', 'OTR script debugging', 'off'),
        ]:
        weechat.config_new_option(
            CONFIG_FILE, CONFIG_SECTIONS['general'], option, typ, desc, '', 0,
            0, default, default, 0, '', '', '', '', '', '')

    CONFIG_SECTIONS['color'] = weechat.config_new_section(
        CONFIG_FILE, 'color', 0, 0, '', '', '', '', '', '', '', '', '', '')

    for option, desc, default in [
        ('status.default', 'status bar default color', 'default'),
        ('status.encrypted', 'status bar encrypted indicator color',
         'lightgreen'),
        ('status.unencrypted', 'status bar unencrypted indicator color',
         'lightred'),
        ('status.authenticated', 'status bar authenticated indicator color',
         'green'),
        ('status.unauthenticated', 'status bar unauthenticated indicator color',
         'red'),
        ]:
        weechat.config_new_option(
            CONFIG_FILE, CONFIG_SECTIONS['color'], option, 'color', desc, '', 0,
            0, default, default, 0, '', '', '', '', '', '')

    CONFIG_SECTIONS['policy'] = weechat.config_new_section(
        CONFIG_FILE, 'policy', 1, 1, '', '', '', '', '', '',
        'policy_create_option_cb', '', '', '')

    for option, desc, default in [
        ('default_allow_v1', 'default allow OTR v1 policy', 'off'),
        ('default_allow_v2', 'default allow OTR v2 policy', 'on'),
        ('default_require_encryption', 'default require encryption policy',
         'off'),
        ('default_send_tag', 'default send tag policy', 'on'),
        ]:
        weechat.config_new_option(
            CONFIG_FILE, CONFIG_SECTIONS['policy'], option, 'boolean', desc, '',
            0, 0, default, default, 0, '', '', '', '', '', '')

    weechat.config_read(CONFIG_FILE)

def config_reload_cb(data, config_file):
    """/reload callback to reload config from file."""
    free_all_config()
    init_config()

    return weechat.WEECHAT_CONFIG_READ_OK

def free_all_config():
    """Free all config options, sections and config file."""
    for section in CONFIG_SECTIONS.itervalues():
        weechat.config_section_free_options(section)
        weechat.config_section_free(section)

    weechat.config_free(CONFIG_FILE)

def create_dir():
    """Create the OTR subdirectory in the WeeChat config directory if it does
    not exist."""
    if not os.path.exists(OTR_DIR):
        weechat.mkdir_home(OTR_DIR_NAME, 0700)

if weechat.register(
    SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENCE, '', 'shutdown',
    ''):
    init_config()

    OTR_DIR = os.path.join(weechat.info_get('weechat_dir', ''), OTR_DIR_NAME)
    create_dir()

    ACCOUNTS = AccountDict()

    weechat.hook_modifier('irc_in_privmsg', 'message_in_cb', '')
    weechat.hook_modifier('irc_out_privmsg', 'message_out_cb', '')

    weechat.hook_command(
        SCRIPT_NAME, SCRIPT_DESC,
        """trust NICK SERVER || smp ask NICK SERVER SECRET [QUESTION] || smp respond NICK SERVER SECRET || endprivate NICK SERVER

To view default OTR policies: /set otr.policy.default*

To set OTR policies for specific users:
/set otr.policy.<server>.<your nick>.<peer nick>.<policy>
""",
        '',
        'endprivate %(nick) %(irc_servers) %-||'
        'smp ask|respond %(nick) %(irc_servers) %-||'
        'trust %(nick) %(irc_servers) %-||',
        'command_cb',
        '')

    OTR_STATUSBAR = weechat.bar_item_new(SCRIPT_NAME, 'otr_statusbar_cb', '')
    weechat.bar_item_update(SCRIPT_NAME)
