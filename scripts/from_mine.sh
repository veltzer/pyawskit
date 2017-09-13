#!/bin/bash -ue

HOST_NAME=MarksZuhause
HOST_NAME=MarksHome

# secrets
scp -r ~/.api-keys.json ~/.pgpass ~/.netrc ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs "$HOST_NAME:" > /dev/null

# pip config
ssh "$HOST_NAME" "mkdir --parents ~/.config/pip" > /dev/null
scp ~/.config/pip/pip.conf "$HOST_NAME:"~/.config/pip > /dev/null

# bash config
scp -r ~/.bashrc ~/.bashy ~/.bash_completion.d "$HOST_NAME:" > /dev/null

# misc
scp -r ~/.hushlogin "$HOST_NAME:" > /dev/null
