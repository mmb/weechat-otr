# weechat-otr - WeeChat script for Off-the-Record messaging
#
# NOTE: This is a work in progress and should not be considered secure.
#
# Copyright (c) 2010 Matthew M. Boedicker <matthewm@boedicker.org>
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

import otr

import weechat

IRC_IN_PRIVMSG_RE = re.compile('(.+?) PRIVMSG (.+?) :(.*)')
IRC_OUT_PRIVMSG_RE = re.compile('PRIVMSG (.+?) :(.*)')

OTR_DIR_NAME = 'otr'
OTR_PREFIX = '?OTR'

PROTOCOL = 'irc'

class AccountNamer:

    def name(self, account, protocol):
        return account

class Commander:

    def command(self, buffer, command):
        weechat.command(buffer, command)

class Informer:

    def __init__(self, nick, server):
        self.buffer = weechat.info_get('irc_buffer', '%s,%s' % (server, nick))

    def inform(self, s):
        weechat.prnt(self.buffer, str(s))

class OtrOps:

    def account_name(self, opdata=None, account=None, protocol=None):
        return opdata['account_namer'].name(account, protocol)

    def create_privkey(self, opdata=None, accountname=None, protocol=None):
        opdata['informer'].inform('generating private key in %s' % KEY_FILE)
        otr.otrl_privkey_generate(USERSTATE, KEY_FILE, accountname, protocol)

    def display_otr_message(self, opdata=None, accountname=None, protocol=None,
                            username=None, msg=None):
        opdata['informer'].inform(msg)

        return 0

    def gone_secure(self, opdata=None, context=None):
        if context and context.active_fingerprint:
            if context.active_fingerprint.trust == 'verified':
                opdata['informer'].inform('verified OTR connection started')
            else:
                opdata['informer'].inform('unverified OTR connection started')

                contact_fingerprint = otr.otrl_privkey_hash_to_human(
                    context.active_fingerprint.fingerprint)
                opdata['informer'].inform("%s's fingerprint is %s" % (
                        opdata['remote_user'], contact_fingerprint))

                your_fingerprint = otr.otrl_privkey_fingerprint(
                    USERSTATE, opdata['local_user'], PROTOCOL)
                opdata['informer'].inform(
                    'your fingerprint is %s' % your_fingerprint)

                opdata['informer'].inform(
                    "please verify %s's fingerprint through a secure channel" %
                    opdata['remote_user'])

    def inject_message(self, opdata=None, accountname=None, protocol=None,
                       recipient=None, message=None):
        nick, server = recipient.split('@', 1)

        opdata['commander'].command(
            '', '/quote -server %s PRIVMSG %s :%s' % (server, nick, message))

    def log_message(self, opdata=None, message=None):
        opdata['informer'].inform(message)

    def max_message_size(self, opdata=None, context=None):
        return 256

    def new_fingerprint(self, opdata=None, userstate=None, accountname=None,
                        protocol=None, username=None, fingerprint=None):
        human_fingerprint = otr.otrl_privkey_hash_to_human(fingerprint)
        opdata['informer'].inform('new fingerprint %s' % human_fingerprint)

    def policy(self, opdata=None, context=None):
        return otr.OTRL_POLICY_DEFAULT

    def update_context_list(self, opdata=None):
        pass

    def write_fingerprints(self, opdata=None):
        opdata['informer'].inform(
            'writing fingerprints to %s' % FINGERPRINT_FILE)
        otr.otrl_privkey_write_fingerprints(USERSTATE, FINGERPRINT_FILE)

def irc_user(nick, server):
    return '%s@%s' % (nick, server)

def current_user(server_name):
    return irc_user(weechat.info_get('irc_nick', server_name), server_name)

def shutdown():
    pass

def otr_irc_in_privmsg(data, message_type, server_name, args):
    result = ''

    match = IRC_IN_PRIVMSG_RE.match(args)
    if match:
        hostmask, channel, message = match.groups()

        nick = weechat.info_get('irc_nick_from_host', hostmask)
        sender = irc_user(nick, server_name)

        opdata = dict(
            account_namer=AccountNamer(),
            commander=Commander(),
            informer=Informer(nick, server_name),
            local_user=current_user(server_name),
            remote_user=sender,
            )

        is_internal, decrypted_message, tlvs = otr.otrl_message_receiving(
            USERSTATE, (OPS, opdata), opdata['local_user'], PROTOCOL, sender,
            message)

        # TODO: check tlvs

        if not is_internal:
            result = '%s PRIVMSG %s :%s' % (hostmask, channel, decrypted_message)
    else:
        weechat.prnt('', 'error parsing privmsg in')

    return result

def otr_irc_out_privmsg(data, message_type, server_name, args):
    result = ''

    match = IRC_OUT_PRIVMSG_RE.match(args)
    if match:
        recipient_nick, message = match.groups()

        if message.startswith(OTR_PREFIX):
            result = args
        else:
            sender = current_user(server_name)

            recipient = irc_user(recipient_nick, server_name)

            informer=Informer(recipient_nick, server_name)

            opdata = dict(
                account_namer=AccountNamer(),
                commander=Commander(),
                informer=informer,
                local_user=sender,
                remote_user=recipient,
                )

            message = otr.otrl_message_sending(
                USERSTATE, (OPS, opdata), sender, PROTOCOL, recipient, message,
                None)

            context, added = otr.otrl_context_find(
                USERSTATE, recipient, sender, PROTOCOL, 1)

            otr.otrl_message_fragment_and_send(
                (OPS, opdata), context, message, otr.OTRL_FRAGMENT_SEND_ALL)

            # TODO: check for return None
    else:
        weechat.prnt('', 'error parsing privmsg out')

    return result

# otr setup
USERSTATE = otr.otrl_userstate_create()
OPS = OtrOps()

# weechat setup
weechat.register(
    'otr', 'Matthew M. Boedicker', '0.0.1', 'GPL3', '', 'shutdown', '')

WEECHAT_DIR = weechat.info_get('weechat_dir', '')
OTR_DIR = os.path.join(WEECHAT_DIR, OTR_DIR_NAME)
if not os.path.exists(OTR_DIR):
    weechat.mkdir_home(OTR_DIR_NAME, 0700)

KEY_FILE = os.path.join(OTR_DIR, 'keys')
if os.path.exists(KEY_FILE):
    otr.otrl_privkey_read(USERSTATE, KEY_FILE)

FINGERPRINT_FILE = os.path.join(OTR_DIR, 'fingerprints')
if os.path.exists(FINGERPRINT_FILE):
    otr.otrl_privkey_read_fingerprints(USERSTATE, FINGERPRINT_FILE)

weechat.hook_modifier('irc_in_privmsg', 'otr_irc_in_privmsg', '')
weechat.hook_modifier('irc_out_privmsg', 'otr_irc_out_privmsg', '')
