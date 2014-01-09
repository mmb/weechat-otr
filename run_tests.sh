#!/bin/sh

pylint --rcfile=pylint.rc weechat_otr.py
pylint --rcfile=pylint.rc weechat_otr_test

python -m unittest discover
