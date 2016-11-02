#!/usr/bin/python3

'''
this script uploads your module to pypi

It does the following:
- clean
- setup.py sdist
- twine upload
- clean again

This script could be done via setuptools using the following:
- python3 setup.py sdist upload -r pypi --identity="Mark Veltzer" --sign
but this has bad security implications as it sends user and password plain text.
This is the reason we use twine(1) to upload the package.
On ubuntu twine(1) is from the 'twine' official ubuntu package.

References:
- https://pypi.python.org/pypi/twine
- https://python-packaging-user-guide.readthedocs.org/en/latest/index.html
'''

import subprocess # for check_call
import os # for listdir
import os.path # for join, expanduser
import common # for git_clean_full, config_file


common.git_clean_full()
subprocess.check_call([
    'python3',
    'setup.py',
    'sdist',
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# at this point there should be only one file in the 'dist' folder
file_list = list(os.listdir('dist'))
assert len(file_list) == 1
filename = file_list[0]
full_filename = os.path.join('dist', filename)
subprocess.check_call([
    'twine',
    'upload',
    full_filename,
#    '--config-file',
#    common.config_file,
])
#], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

common.git_clean_full()
