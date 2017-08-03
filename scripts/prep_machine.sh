#!/bin/bash -ue

# This script does the basic stuff on the machine

export DEBIAN_FRONTEND=noninteractive
export APT_QUIET_FLAGS=-yq
sudo apt $APT_QUIET_FLAGS update
sudo apt $APT_QUIET_FLAGS dist-upgrade
sudo apt $APT_QUIET_FLAGS auto-remove
# a reboot may be necessary if a new kernel was installed
sudo apt $APT_QUIET_FLAGS install python-pip python-dev python3-pip python3-dev git apt-file awscli s3cmd s3fs zip tree jq parallel mdadm lrzip bc sqlite3 pipemeter awscli postgresql-client-common postgresql-client-9.5 virtualenv virtualenvwrapper dialog libenchant-dev libssl-dev

sudo -H pip install pip --upgrade
sudo -H pip3 install pip --upgrade

mkdir --parents ~/.config/pip
sudo mkdir --parents /root/.config/pip

# set the hostname of the machine (it's usually hostname is ip-XXX-XXX-XXX-XXX).
HOST_NAME="MarksHome"
HOST_NAME="MarksZuhause"
sudo sh -c "echo 127.0.0.1 $HOST_NAME >> /etc/hosts"
sudo sh -c "echo $HOST_NAME > /etc/hostname"
sudo hostname "$HOST_NAME"
