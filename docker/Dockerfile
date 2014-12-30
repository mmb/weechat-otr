FROM ubuntu

RUN apt-get update
RUN apt-get --assume-yes install build-essential
RUN apt-get --assume-yes install pylint
RUN apt-get --assume-yes install python-dev
RUN apt-get --assume-yes install python-setuptools

RUN easy_install pip
RUN pip install python-potr
