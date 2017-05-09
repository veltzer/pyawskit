#!/usr/bin/env bash

# these are the things to be done even before we run any python as this
# is a pre-requisite to the python code...

# this whole script should be run by root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

apt-get update
apt-get upgrade
apt-get install python3-pip awscli vim
echo 127.0.0.1 `hostname` >> /etc/hosts