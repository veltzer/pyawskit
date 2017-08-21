#!/bin/bash -ue

# This script does the basic stuff on the machine
# must be run with sudo

if [ "$EUID" -ne 0 ]
	then
	echo "Please run as root"
	exit
fi

export DEBIAN_FRONTEND=noninteractive
export APT_QUIET_FLAGS=-yq
apt $APT_QUIET_FLAGS update
apt $APT_QUIET_FLAGS dist-upgrade
apt $APT_QUIET_FLAGS auto-remove
# a reboot may be necessary if a new kernel was installed
apt $APT_QUIET_FLAGS install python-pip python-dev python3-pip python3-dev git apt-file awscli s3cmd s3fs zip tree jq parallel mdadm lrzip bc sqlite3 pipemeter awscli postgresql-client-common postgresql-client-9.5 virtualenv virtualenvwrapper dialog libenchant-dev libssl-dev pigz tree lmdb-utils ansible moreutils

pip install pip --upgrade
pip3 install pip --upgrade

# set the hostname of the machine (it's usually hostname is ip-XXX-XXX-XXX-XXX).
HOST_NAME="MarksHome"
# HOST_NAME="MarksZuhause"
echo 127.0.0.1 $HOST_NAME >> /etc/hosts
echo $HOST_NAME > /etc/hostname
hostname "$HOST_NAME"
