#!/bin/bash -ue

# This script does the basic stuff on the machine

sudo apt -y update
sudo apt -y dist-upgrade
sudo apt -y auto-remove
# a reboot may be necessary if a new kernel was installed
sudo apt -y install python-pip python-dev python3-pip python3-dev git apt-file awscli s3cmd s3fs zip tree jq parallel mdadm lrzip bc sqlite3 pipemeter awscli postgresql-client-common postgresql-client-9.5 virtualenv virtualenvwrapper
sudo -H pip install pip --upgrade
sudo -H pip3 install pip --upgrade
mkdir --parents ~/.config/pip
sudo mkdir --parents /root/.config/pip
# set the hostname of the machine (it's usually hostname is ip-XXX-XXX-XXX-XXX).
HOST_NAME="MarksHome"
sudo sh -c "echo $HOST_NAME  > /etc/hostname"
sudo hostname "$HOST_NAME"
# TBD: change /etc/hosts
# set quiet login
touch ~/.hushlogin
