#!/usr/bin/python3

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

import subprocess # for check_output, check_call
import os # for geteuid
import sys # for exit
import enum  # for Enum
from typing import List

class OSType(enum.Enum):
    ubuntu=1
    aml=2

def run(args: List[str]):
    #print('running', args)
    subprocess.check_call(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

os_type=None
# first find out if we are on ubuntu or amazon linux
def detect_os():
    global os_type
    try:
        if subprocess.check_output(['lsb_release','--id','-s']).decode().rstrip()=='Ubuntu':
            os_type=OSType.ubuntu
    except:
        pass
    try:
        with open('/etc/issue') as f:
            d=f.read()
            if d.startswith('Amazon Linux AMI'):
                os_type=OSType.aml
    except:
        pass

    if os_type is None:
        sys.exit('could not detect the os running')

def is_os_type(t):
    global os_type
    return os_type == t

# check that we are running as root
def check_root():
    if not os.geteuid() == 0:
        sys.exit('script must be run as root')

def update_machine():
    if is_os_type(OSType.ubuntu):
        run(['apt-get','update'])
        run(['apt-get','upgrade'])
    if is_os_type(OSType.aml):
        run(['yum','update'])
        run(['yum','upgrade'])


check_root()
detect_os()
update_machine()

####### fix the code from here #######

# install neccessary package per platform

list_of_packages={
    OSType.ubuntu: [
        'python-pip',
        'python-dev',
        'python3-pip',
        'python3-dev',
        'git',
        'parallel',
        'jq',
        'tree',
        'zip',
    ],
    OSType.aml: [
    ],
}

# install the packages
#subprocess.check_call([
#])
