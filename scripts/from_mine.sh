#!/bin/bash -ue

# HOST_NAME=MarksHome
HOST_NAME=MarksZuhause
scp -r ~/.pgpass ~/.netrc ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs $HOST_NAME: > /dev/null
scp ~/.config/pip/pip.conf $HOST_NAME:~/.config/pip > /dev/null
scp -r ~/.bashrc.d ~/.bashy ~/.bashrc $HOST_NAME: > /dev/null
scp -r ~/.hushlogin $HOST_NAME: > /dev/null
# scp ~/.config/pip/pip.conf $HOST_NAME:/root/.config/pip > /dev/null
