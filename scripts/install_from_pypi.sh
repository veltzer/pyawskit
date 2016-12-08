#!/bin/sh

PIP=pip
PIP=pip3
sudo -H ${PIP} install --quiet --upgrade awskit
${PIP} show awskit | grep -e "^Version"
