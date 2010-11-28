# weechat-otr - WeeChat script for Off-the-Record messaging
#
# See http://www.cypherpunks.ca/otr/

# Copyright (c) 2010 Matthew M. Boedicker <matthewm@boedicker.org>
#
# NOTE: integration with OTR is not done yet, will use Python bindings for
# libotr at http://python-otr.pentabarf.de/
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

import re

import weechat

IRC_IN_PRIVMSG_RE = re.compile('(.+) PRIVMSG (.+) :(.*)')
IRC_OUT_PRIVMSG_RE = re.compile('PRIVMSG (.+) :(.*)')

def shutdown():
  pass

def otr_irc_in_privmsg(data, message_type, server_name, args):
  match = IRC_IN_PRIVMSG_RE.match(args)
  if match:
    hostmask, channel, message = match.groups()
    # decrypt message with otr
    return '%s PRIVMSG %s :%s' % (
      hostmask, channel, 'not integrated with OTR yet')
  else:
    weechat.prnt('', 'error parsing privmsg in')

def otr_irc_out_privmsg(data, message_type, server_name, args):
  match = IRC_OUT_PRIVMSG_RE.match(args)
  if match:
    recipient, message = match.groups()
    # encrypt message with otr
    return 'PRIVMSG %s :%s' % (recipient, 'not integrated with OTR yet')
  else:
    weechat.prnt('', 'error parsing privmsg out')

weechat.register(
  'otr', 'Matthew M. Boedicker', '0.0.1', 'GPL3', '', 'shutdown', '')

weechat.hook_modifier('irc_in_privmsg', 'otr_irc_in_privmsg', '')
weechat.hook_modifier('irc_out_privmsg', 'otr_irc_out_privmsg', '')
