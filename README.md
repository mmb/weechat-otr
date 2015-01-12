[![Build Status](https://travis-ci.org/mmb/weechat-otr.png)](https://travis-ci.org/mmb/weechat-otr)

WeeChat script for Off-the-Record messaging

DISCLAIMER: This script makes every effort to securely provide OTR
messaging in WeeChat but offers no guarantee. Please report any security
holes you find.

Testing and security auditing are appreciated.

#Installation

This script requires Weechat 0.4.2 or later and the
[Pure Python OTR](https://github.com/afflux/pure-python-otr)
package to be installed:

`pip install --user python-potr`

The latest release version of WeeChat OTR can be found in the
[WeeChat scripts repository](https://www.weechat.org/scripts/source/otr.py.html/).

To install manually, download `weechat_otr.py` from GitHub and save it in
`~/.weechat/python`. Then either symlink it into
`~/.weechat/python/autoload` or `/python load python/weechat_otr.py`
in WeeChat.

[Latest unstable version from GitHub](https://raw.githubusercontent.com/mmb/weechat-otr/master/weechat_otr.py)

#Support

IRC channel: #weechat-otr on Freenode

Create GitHub issues/pull requests for questions, comments and patches or
email matthewm@boedicker.org or koolfy@koolfy.be.

#Thanks

Thanks to Kjell Braden for the Pure Python OTR library and the Gajim
Python plugin which was used as a reference.
