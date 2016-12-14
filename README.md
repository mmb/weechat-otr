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
package to be installed with one of the following methods:

Python package:
```bash
pip install --upgrade --user python-potr
```

If this fails, read
[Requirements for building Pure Python OTR](#requirements-for-building-pure-python-otr)
below.

Arch:
```bash
yaourt -S python2-potr
```

Debian based systems:
```bash
sudo apt-get install python-potr
```

The latest release version of WeeChat OTR can be found in the
[WeeChat scripts repository](https://www.weechat.org/scripts/source/otr.py.html/).
To install from within WeeChat:

    /script install otr.py

To install manually, download `weechat_otr.py` from GitHub and save it in
`~/.weechat/python`. Then either symlink it into
`~/.weechat/python/autoload` or `/python load weechat_otr.py`
in WeeChat.

[Latest unstable version from GitHub](https://raw.githubusercontent.com/mmb/weechat-otr/master/weechat_otr.py)

If you are using an official release of the script, it is a good idea to
[verify the signature](https://s3.amazonaws.com/weechat-otr-signatures/index.html).

### Requirements for building Pure Python OTR

If python-potr fails to install, you are probably missing some packages.
To install all the requirements on a Debian/Ubuntu system, run

    sudo apt-get install python-pip python-wheel build-essential python-dev

Or on Arch run

    sudo pacman --needed -S python2-pip python2-wheel python2-keyring base-devel

## Buffer Local Variables

The script will set the following buffer local variables:

- `localvar_set_otr_encrypted` - whether the buffer is OTR encrypted (true or false)
- `localvar_set_otr_authenticated` - whether the buffer is OTR authenticated (true or false)
- `localvar_set_otr_logged` - whether the buffer is logged (true or false)

These match what is shown in the status bar and can be used by remote interfaces
via the WeeChat relay protocol or by other scripts.

## Support

IRC channel: `#weechat-otr` on Freenode

Create GitHub issues/pull requests for questions, comments and patches or
email matthewm@boedicker.org or koolfy@koolfy.be.

## Thanks

Thanks to Kjell Braden for the Pure Python OTR library and the Gajim
Python plugin which was used as a reference.
