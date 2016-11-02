#!/bin/sh

sudo -H pip3 install --quiet --upgrade awskit
#sudo -H pip install --quiet --upgrade awskit
pip3 show awskit | grep -e "^Version"
