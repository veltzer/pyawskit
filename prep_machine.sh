#!/bin/bash

: '

This script does the basic stuff on the machine

After this script is done download any packages you want.
Install requirements using
$ pip3 install -r requirements.txt
'

/usr/bin/pip install --upgrade pip
/usr/bin/pip3 install --upgrade pip
sudo apt-get install python-pip python-dev python3-pip python3-dev git apt-file awscli s3cmd s3fs zip tree jq parallel mdadm lrzip bc