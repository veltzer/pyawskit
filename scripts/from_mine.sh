#!/bin/bash -ue

HOST_NAME=MarksHome
# HOST_NAME=MarksZuhause
scp -r ~/.api-keys.json ~/.pgpass ~/.netrc ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs $HOST_NAME: > /dev/null
ssh $HOST_NAME "mkdir --parents ~/.config/pip"
scp ~/.config/pip/pip.conf $HOST_NAME:~/.config/pip > /dev/null
scp -r ~/.bashrc ~/.bashy $HOST_NAME: > /dev/null
scp -r ~/.hushlogin $HOST_NAME: > /dev/null
# scp ~/.config/pip/pip.conf $HOST_NAME:/root/.config/pip > /dev/null
