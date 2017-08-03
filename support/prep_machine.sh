#!/bin/bash

: '

This script does the basic stuff on the machine

After this script is done download any packages you want.
Install requirements using
$ pip3 install -r requirements.txt
'

ssh MarksHome "sudo apt-get install python-pip python-dev python3-pip python3-dev git apt-file awscli s3cmd s3fs zip tree jq parallel mdadm lrzip bc sqlite3 pipemeter"
ssh MarksHome "apt-get update"
ssh MarksHome "apt-get dist-upgrade"
# a reboot may be necessary if a new kernel was installed
ssh MarksHome "apt install python3-pip python3-dev python-pip python-dev"
ssh MarksHome "sudo -H pip install pip --upgrade"
ssh MarksHome "sudo -H pip3 install pip --upgrade"
scp -r ~/.pgpass ~/.netrc ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs MarksHome:~
ssh MarksHome "mkdir --parents ~/.config/pip"; scp ~/.config/pip/pip.conf MarksHome:~/.config/pip
ssh MarksHome "mkdir --parents /root/.config/pip"; scp ~/.config/pip/pip.conf MarksHome:/root/.config/pip
# set the hostname of the machine (it's usually hostname is ip-XXX-XXX-XXX-XXX).
ssh MarksHome "echo MarksHome  > /etc/hostname"
# set quiet login using:
ssh MarksHome "touch ~/.hushlogin"
