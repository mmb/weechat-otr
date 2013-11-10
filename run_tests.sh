#!/bin/sh

pylint weechat_otr.py test
pylint test

python -m unittest discover
