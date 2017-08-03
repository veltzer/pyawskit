#!/bin/bash

scp -r ~/.pgpass ~/.netrc ~/.aws ~/.ssh ~/.s3cfg ~/.gitconfig ~/.passwd-s3fs MarksHome:~
scp ~/.config/pip/pip.conf MarksHome:~/.config/pip
scp ~/.config/pip/pip.conf MarksHome:/root/.config/pip
