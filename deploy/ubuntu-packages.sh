#!/bin/bash

# ubuntu packages necessary to get virtual environment installed correctly

apt-get install git-core
apt-get install python-virtualenv
apt-get install gcc
apt-get install build-essential
apt-get install libssl-dev
apt-get install python-imaging
apt-get install python-dev
apt-get instlal python-lxml
apt-get install python-mysqldb
apt-get install emacs23
dpkg --list | awk '{print $2}' | grep ^pyt | xargs echo apt-get install