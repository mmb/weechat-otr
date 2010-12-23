# weechat-otr - WeeChat script for Off-the-Record messaging
#
# DISCLAIMER: To the best of my knowledge this script securely provides OTR
# messaging in WeeChat, but I offer no guarantee. Please report any security
# holes you find.
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
OTR_QUERY_RE = re.compile('\?OTR\??v[a-z\d]*\?$')

PROTOCOL = 'irc'

class AccountNamer:

    def name(self, account, protocol):
        return account

class Assembler:
    """Reassemble fragmented OTR messages.

    This does not deal with OTR fragmentation, which is handled by the otr
    module, but fragmentation of received OTR messages that are too large for
    IRC (bitlbee does this).
    """
    def __init__(self):
        self.__clear()

    def add(self, s):
        self.value += s

    def __is_query(self):
        return OTR_QUERY_RE.match(self.value)

    def done(self):
        return self.__is_query() or \
            not self.value.startswith(OTR_PREFIX) or \
            self.value.endswith('.') or \
            self.value.endswith(',')

    def get(self):
        result = self.value
        self.__clear()

        return result

    def __clear(self):
        self.value = ''

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
        opdata['informer'].inform('Generating private key in %s' % KEY_FILE)
        otr.otrl_privkey_generate(USERSTATE, KEY_FILE, accountname, protocol)

    def display_otr_message(self, opdata=None, accountname=None, protocol=None,
                            username=None, msg=None):
        opdata['informer'].inform(msg)

        return 0

    def gone_secure(self, opdata=None, context=None):
        if context and context.active_fingerprint:
            if context.active_fingerprint.trust == 'verified':
                opdata['informer'].inform('Verified OTR connection started')
            else:
                opdata['informer'].inform('Unverified OTR connection started')
                otr_verify_instructions(opdata, context)
        else:
            opdata['informer'].inform('Invalid context')

    def inject_message(self, opdata=None, accountname=None, protocol=None,
                       recipient=None, message=None):
        nick, server = recipient.split('@', 1)

        opdata['commander'].command(
            '', '/quote -server %s PRIVMSG %s :%s' % (server, nick, message))

    def log_message(self, opdata=None, message=None):
        opdata['informer'].inform(message)

    def max_message_size(self, opdata=None, context=None):
        # see http://www.cypherpunks.ca/otr/UPGRADING-libotr-3.2.0.txt
        # section 3.1.1
        return 417

    def new_fingerprint(self, opdata=None, userstate=None, accountname=None,
                        protocol=None, username=None, fingerprint=None):
        human_fingerprint = otr.otrl_privkey_hash_to_human(fingerprint)
        opdata['informer'].inform('New fingerprint %s' % human_fingerprint)

    def policy(self, opdata=None, context=None):
        return otr.OTRL_POLICY_DEFAULT

    def still_secure(self, opdata=None, context=None, is_reply=None):
        # TODO find out what this is for
        opdata['informer'].inform('Still secure %s' % is_reply)

    def update_context_list(self, opdata=None):
        pass

    def write_fingerprints(self, opdata=None):
        opdata['informer'].inform(
            'Writing fingerprints to %s' % FINGERPRINT_FILE)
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

        opdata = otr_opdata(nick, server_name)

        context = otr_context_find(sender, opdata['local_user'])

        assembler = context.app_data['assembler']

        assembler.add(message)

        if assembler.done():
            is_internal, decrypted_message, tlvs = otr.otrl_message_receiving(
                USERSTATE, (OPS, opdata), opdata['local_user'], PROTOCOL,
                sender, assembler.get())

            if context.smstate:
                otr_check_tlvs(opdata, tlvs, context)
            else:
                opdata['informer'].inform('Invalid context')

            if not is_internal:
                result = '%s PRIVMSG %s :%s' % (
                    hostmask, channel, decrypted_message)
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

            opdata = otr_opdata(recipient_nick, server_name)

            message = otr.otrl_message_sending(
                USERSTATE, (OPS, opdata), sender, PROTOCOL, recipient, message,
                None)

            context = otr_context_find(recipient, sender)

            otr.otrl_message_fragment_and_send(
                (OPS, opdata), context, message, otr.OTRL_FRAGMENT_SEND_ALL)

            # TODO: check for return None
    else:
        weechat.prnt('', 'error parsing privmsg out')

    return result

def otr_command(data, buffer, args):
    result = weechat.WEECHAT_RC_ERROR

    arg_parts = args.split(None, 5)

    if arg_parts[0] == 'trust':
        otr_trust(*arg_parts[1:3])
        result = weechat.WEECHAT_RC_OK
    elif arg_parts[0] == 'smp':
        action = arg_parts[1]
        if action == 'respond':
            nick, server, secret = arg_parts[2:5]
            otr_smp_respond(nick, server, secret)
            result = weechat.WEECHAT_RC_OK
        elif action == 'ask':
            nick, server, secret = arg_parts[2:5]
            if len(arg_parts) > 5:
                question = arg_parts[5]
            else:
                question = None
            otr_smp_ask(nick, server, secret, question)
            result = weechat.WEECHAT_RC_OK
    elif arg_parts[0] == 'endprivate':
        nick, server = arg_parts[1:3]
        context = otr_context_find(irc_user(nick, server), current_user(server))
        otr.otrl_context_force_plaintext(context)
        result = weechat.WEECHAT_RC_OK

    return result

def otr_add_app_data(data=None, context=None):
    context.app_data = dict(assembler=Assembler())

def otr_context_find(remote_user, local_user, add=1):
    return otr.otrl_context_find(
        USERSTATE, remote_user, local_user, PROTOCOL, add,
        (otr_add_app_data, None))[0]

def otr_check_tlvs(opdata, tlvs, context):
    if otr.otrl_tlv_find(tlvs, otr.OTRL_TLV_SMP_ABORT):
        opdata['informer'].inform('SMP was aborted')
    else:
        smp1q_tlv = otr.otrl_tlv_find(tlvs, otr.OTRL_TLV_SMP1Q)

        if context.smstate.sm_prog_state == otr.OTRL_SMP_PROG_CHEATED:
            otr_smp_abort(opdata, context, 'cheated')

        elif otr.otrl_tlv_find(tlvs, otr.OTRL_TLV_SMP1):
            if otr_expect_smstate(opdata, context, otr.OTRL_SMP_EXPECT1):
                opdata['informer'].inform(
                    '%(remote_user)s has requested SMP verification' % opdata)
                opdata['informer'].inform(
                    'Respond with /otr smp respond %(remote_user)s %(server)s <secret>' % opdata)

        elif smp1q_tlv:
            if otr_expect_smstate(opdata, context, otr.OTRL_SMP_EXPECT1):
                opdata['informer'].inform(
                    '%s has requested SMP verification: %s' % (
                        opdata['remote_user'], smp1q_tlv.data))
                opdata['informer'].inform(
                    'Respond with /otr smp respond %(remote_user)s %(server)s <answer>' % opdata)

        elif otr.otrl_tlv_find(tlvs, otr.OTRL_TLV_SMP2):
            if otr_expect_smstate(opdata, context, otr.OTRL_SMP_EXPECT2):
                context.smstate.nextExpected = otr.OTRL_SMP_EXPECT4
                opdata['informer'].inform('SMP progressing')

        elif otr.otrl_tlv_find(tlvs, otr.OTRL_TLV_SMP3):
            if otr_expect_smstate(opdata, context, otr.OTRL_SMP_EXPECT3):
                context.smstate.nextExpected = otr.OTRL_SMP_EXPECT1
                otr_smp_inform(opdata, context)

        elif otr.otrl_tlv_find(tlvs, otr.OTRL_TLV_SMP4):
            if otr_expect_smstate(opdata, context, otr.OTRL_SMP_EXPECT4):
                context.smstate.nextExpected = otr.OTRL_SMP_EXPECT1
                otr_smp_inform(opdata, context)

def otr_expect_smstate(opdata, context, state):
    if state == context.smstate.nextExpected:
        return True
    else:
        otr_smp_abort(opdata, context, 'expecting smstate %s not %s' % (
                context.smstate.nextExpected, state))
        return False

def otr_opdata(remote_user, server):
    return dict(
        account_namer=AccountNamer(),
        commander=Commander(),
        informer=Informer(remote_user, server),
        local_user=current_user(server),
        remote_user=remote_user,
        server=server,
        )

def otr_smp_abort(opdata, context, detail=None):
    message = 'Aborting SMP'
    if detail:
        message += ', %s' % detail
    opdata['informer'].inform(message)
    otr.otrl_message_abort_smp(USERSTATE, (OPS, opdata), context)

def otr_smp_ask(nick, server, secret, question=None):
    context = otr_context_find(irc_user(nick, server), current_user(server))

    opdata = otr_opdata(nick, server)

    if question:
        otr.otrl_message_initiate_smp_q(
            USERSTATE, (OPS, opdata), context, question, secret)
    else:
        otr.otrl_message_initiate_smp(USERSTATE, (OPS, opdata), context, secret)

def otr_smp_inform(opdata, context):
    if context.smstate.sm_prog_state == otr.OTRL_SMP_PROG_SUCCEEDED:
        message = 'SMP verification succeeded'
    else:
        message = 'SMP verification failed'

    opdata['informer'].inform(message)

def otr_smp_respond(nick, server, secret):
    context = otr_context_find(irc_user(nick, server), current_user(server))

    otr.otrl_message_respond_smp(
        USERSTATE, (OPS, otr_opdata(nick, server)), context, secret)

def otr_trust(nick, server):
    context = otr_context_find(irc_user(nick, server), current_user(server), 0)

    if context and context.active_fingerprint:
	context.active_fingerprint.trust = 'verified'
	otr.otrl_privkey_write_fingerprints(USERSTATE, FINGERPRINT_FILE)

def otr_verify_instructions(opdata=None, context=None):
    d = dict(
        remote_fingerprint=otr.otrl_privkey_hash_to_human(
            context.active_fingerprint.fingerprint),
        remote_user=opdata['remote_user'],
        server=opdata['server'],
        your_fingerprint=otr.otrl_privkey_fingerprint(
            USERSTATE, opdata['local_user'], PROTOCOL))

    instructions = """
You can verify that this contact is who they claim to be in one of 3 ways:

1) Verify that these fingerprints match using a secure channel:
  Your fingerprint : %(your_fingerprint)s
  %(remote_user)s's fingerprint : %(remote_fingerprint)s

  then use the command: /otr trust %(remote_user)s %(server)s

2) SMP shared secret:
  /otr smp ask %(remote_user)s %(server)s <secret>

3) SMP shared secret with question:
  /otr smp ask %(remote_user)s %(server)s <secret> <question>
""" % d

    for line in instructions.split("\n"):
        opdata['informer'].inform(line)

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
    otr.otrl_privkey_read_fingerprints(
        USERSTATE, FINGERPRINT_FILE, (otr_add_app_data, None))

weechat.hook_modifier('irc_in_privmsg', 'otr_irc_in_privmsg', '')
weechat.hook_modifier('irc_out_privmsg', 'otr_irc_out_privmsg', '')

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
