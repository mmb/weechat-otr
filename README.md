[![Build Status](https://travis-ci.org/mmb/weechat-otr.png)](https://travis-ci.org/mmb/weechat-otr)

WeeChat script for Off-the-Record messaging

DISCLAIMER: To the best of my knowledge this script securely provides OTR
messaging in WeeChat, but I offer no guarantee. Please report any security
holes you find.

Testing and security auditing are appreciated.

It requires the most recent master branch of the pure Python OTR
implementation (potr):

https://github.com/afflux/pure-python-otr

Thanks to Kjell Braden for the Python OTR library and the Gajim Python plugin
which I used as a reference.

To install script:

Copy weechat_otr.py to ~/.weechat/python/

Then either symlink it into ~/.weechat/python/autoload
or '/python load python/weechat_otr.py' in WeeChat

Questions, comments and patches welcome: matthewm@boedicker.org
Current maintainer: koolfy@koolfy.be

Feel free to open issues on Github before sending an email.
