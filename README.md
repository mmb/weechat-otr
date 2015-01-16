# WeeChat script for Off-the-Record (OTR) Messaging

![Screenshot](https://cloud.githubusercontent.com/assets/24275/5772021/262c6dd6-9cff-11e4-964f-1812a6a545c6.png)

> **Please note**: This script makes every effort to securely provide OTR
> Messaging in WeeChat but offers no guarantee. Please report any security
> problems you find.

Testing and security auditing are appreciated.

[![Build Status](https://travis-ci.org/mmb/weechat-otr.svg?branch=master)](https://travis-ci.org/mmb/weechat-otr)

## Installation

This script requires Weechat 0.4.2 or later and the
[Pure Python OTR](https://github.com/afflux/pure-python-otr)
package to be installed (see below if this command fails):

    pip install --upgrade --user python-potr

The latest release version of WeeChat OTR can be found in the
[WeeChat scripts repository](https://www.weechat.org/scripts/source/otr.py.html/).
To install from within WeeChat:

    /script install otr.py

To install manually, download `weechat_otr.py` from GitHub and save it in
`~/.weechat/python`. Then either symlink it into
`~/.weechat/python/autoload` or `/python load weechat_otr.py`
in WeeChat.

[Latest unstable version from GitHub](https://raw.githubusercontent.com/mmb/weechat-otr/master/weechat_otr.py)

### Requirements for building Pure Python OTR

If python-potr fails to install, you are probably missing some packages.
To install all the requirements on a Debian/Ubuntu system, run

    sudo apt-get install python-pip build-essential python-dev

## Support

IRC channel: `#weechat-otr` on Freenode

Create GitHub issues/pull requests for questions, comments and patches or
email matthewm@boedicker.org or koolfy@koolfy.be.

## Thanks

Thanks to Kjell Braden for the Pure Python OTR library and the Gajim
Python plugin which was used as a reference.
