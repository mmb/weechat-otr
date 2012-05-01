# weechat-otr - WeeChat script for Off-the-Record messaging
#
# DISCLAIMER: To the best of my knowledge this script securely provides OTR
# messaging in WeeChat, but I offer no guarantee. Please report any security
# holes you find.
#
# Copyright (c) 2012 Matthew M. Boedicker <matthewm@boedicker.org>
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

import os
import re

import weechat

import potr

OTR_DIR_NAME = 'otr'
OTR_QUERY_RE = re.compile('\?OTR\??v[a-z\d]*\?$')

ACCOUNTS = {}

DEBUG = True

def debug(msg):
    """Send a debug message to the WeeChat core buffer."""
    if DEBUG:
        weechat.prnt('OTR debug: %s', str(msg))

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
            self.value.endswith('.') or \
            self.value.endswith(',')

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

    def getPolicy(self, key):
        debug('get policy %s' % key)

        return {
            'ALLOW_V1' : True,
            'ALLOW_V2' : True,
            'REQUIRE_ENCRYPTION' : True,
            'SEND_TAG' : True,
            }[key]

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

        if self.state == potr.context.STATE_ENCRYPTED:
            if newstate == potr.context.STATE_ENCRYPTED:
                self.print_buffer(
                    'Private conversation has been refreshed.')
            elif newstate == potr.context.STATE_FINISHED:
                self.print_buffer(
                    'Remote peer has ended the private conversation. You should do the same.')
        elif newstate == potr.context.STATE_ENCRYPTED:
            # unencrypted => encrypted
            trust = self.getCurrentTrust()
            if trust is None:
                fpr = str(self.getCurrentKey())
                self.print_buffer('New fingerprint: %s' % fpr)
                self.setCurrentTrust('')

            if bool(trust):
                trust_str = 'Authenticated'
            else:
                trust_str = 'Unauthenticated'

            self.print_buffer(
                '%s secured OTR conversation started.' % trust_str)

        if self.state != potr.context.STATE_PLAINTEXT and \
                newstate == potr.context.STATE_PLAINTEXT:
            self.print_buffer('Private conversation ended.')

        super(IrcContext, self).setState(newstate)

    def buffer(self):
        """Get the buffer for this context."""
        return weechat.info_get(
            'irc_buffer', '%s,%s' % (self.peer_server, self.peer_nick))

    def print_buffer(self, msg):
        """Print a message to the buffer for this context."""
        weechat.prnt(self.buffer(), msg)

class IrcOtrAccount(potr.context.Account):
    """Account class for OTR over IRC."""

    contextclass = IrcContext

    PROTOCOL = 'irc'
    MAX_MSG_SIZE = 417

    def __init__(self, name):
        super(IrcOtrAccount, self).__init__(
            name, IrcOtrAccount.PROTOCOL, IrcOtrAccount.MAX_MSG_SIZE)

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

def message_in(data, modifier, modifier_data, string):
    """Incoming message callback"""
    debug(('message_in', data, modifier, modifier_data, string))

    parsed = weechat.info_get_hashtable(
        'irc_message_parse', dict(message=string))
    debug(('parsed message', parsed))

    msg_text = extract_privmsg_text(parsed['arguments'])

    server = modifier_data

    from_user = irc_user(parsed['nick'], server)
    local_user = current_user(server)

    if local_user not in ACCOUNTS:
        debug(('add account', local_user))
        ACCOUNTS[local_user] = IrcOtrAccount(local_user)

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
        except potr.context.UnencryptedMessage, e:
            result = string
        except potr.context.NotEncryptedError, e:
            context.print_buffer(
                'Received encrypted data but no private session established.')

    return result

def message_out(data, modifier, modifier_data, string):
    """Outgoing message callback."""
    debug(('message_out', data, modifier, modifier_data, string))

    parsed = weechat.info_get_hashtable(
        'irc_message_parse', dict(message=string))
    debug(('parsed message', parsed))

    msg_text = extract_privmsg_text(parsed['arguments'])

    server = modifier_data

    to_user = irc_user(parsed['nick'], server)
    local_user = current_user(server)

    if local_user not in ACCOUNTS:
        ACCOUNTS[local_user] = IrcOtrAccount(local_user)

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

        context.sendMessage(
            potr.context.FRAGMENT_SEND_ALL, msg_text,
            appdata=dict(nick=parsed['nick'], server=server))

        result = ''

    return result

def shutdown():
    """Script unload callback."""
    debug('shutdown')

    return weechat.WEECHAT_RC_OK

weechat.register(
    'otr', 'Matthew M. Boedicker', '0.0.2', 'GPL3', '', 'shutdown', '')

WEECHAT_DIR = weechat.info_get('weechat_dir', '')
OTR_DIR = os.path.join(WEECHAT_DIR, OTR_DIR_NAME)
if not os.path.exists(OTR_DIR):
    weechat.mkdir_home(OTR_DIR_NAME, 0700)

weechat.hook_modifier('irc_in_privmsg', 'message_in', '')
weechat.hook_modifier('irc_out_privmsg', 'message_out', '')

weechat.hook_command(
    'otr', 'Off-the-Record',
    '[trust nick server] | '
    '[smp respond nick server secret] | '
    '[smp ask nick server secret [question]]'
    '[endprivate nick server]',
    '',
    '',
    'otr_command',
    '')
