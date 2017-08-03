#!/bin/bash -ue

# HOST_NAME=MarksHome
HOST_NAME=MarksZuhause
scp -r ~/.pgpass ~/.netrc ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs MarksHome: > /dev/null
scp ~/.config/pip/pip.conf MarksHome:~/.config/pip > /dev/null
scp -r ~/.bashrc.d ~/.bashy ~/.bashrc MarksHome: > /dev/null
scp -r ~/.hushlogin MarksHome: > /dev/null
# scp ~/.config/pip/pip.conf MarksHome:/root/.config/pip > /dev/null
