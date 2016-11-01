#!/usr/bin/python

'''
A python version of the script here:
-https://gist.github.com/joemiller/6049831

- apt-get update
- apt-get dist-upgrade
- install a list of packages on the system:
- format and mount all disks
    use madm
- copy ~/.aws to it
- copy keys from ~/.ssh to it
- copy ~/.gitconfig to it.
- set the hostname of the machine (it's usualy hostname is ip-XXX-XXX-XXX-XXX).
- configure vim to do correct python editing and save editing positions.
'''

import subprocess
import os
import sys

# check that we are running as root
if not os.geteuid() == 0:
    sys.exit('Script must be run as root')

# first find out if we are on ubuntu or amazon linux

os_type=None
try:
    if subprocess.check_output(['lsb_release','--id','-s']).rstrip()=='Ubuntu':
        os_type='ubuntu'
except:
    pass
try:
    with open('/etc/issue') as f:
        d=f.read()
        if d.startswith('Amazon Linux AMI'):
            os_type='amazon_linux'
except:
    pass

if os_type is None:
    sys.exit('could not detect the os running')

# install neccessary package per platform

list_of_packages_ubuntu=[
        'python-pip',
        'python-dev',
	'python3-pip',
	'python3-dev',
	'git',
	'parallel',
	'jq',
	'tree',
	'zip',
]

list_of_package_aml=[
]

#subprocess.check_call([
#)
