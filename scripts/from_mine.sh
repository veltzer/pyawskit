#!/bin/bash -ue

scp -r ~/.pgpass ~/.netrc ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs MarksHome:~ > /dev/null
scp ~/.config/pip/pip.conf MarksHome:~/.config/pip > /dev/null
# scp ~/.config/pip/pip.conf MarksHome:/root/.config/pip
