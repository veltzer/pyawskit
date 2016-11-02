#!/usr/bin/python3

'''
This script registers your project via twine.

It does:
- full clean
- build wheel using setup.py
- twine register
- full clean

NOTE!!!
- It seems that registering packages is no longer supported. Just upload the package.
This is the error that I got:
Registering package to https://upload.pypi.org/legacy/
Registering awskit-0.0.1-py2.py3-none-any.whl
HTTPError: 410 Client Error: This API is no longer supported, instead simply upload the file.

References:
- https://packaging.python.org/distributing/
'''

import common # for git_clean_full
import subprocess # for check_call, DEVNULL
import os # for listdir

common.git_clean_full()
subprocess.check_call([
    'python3',
    'setup.py',
    'bdist_wheel',
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# at this point there should be only one file in the 'dist' folder
file_list = list(os.listdir('dist'))
assert len(file_list) == 1
filename = file_list[0]
full_filename = os.path.join('dist', filename)
subprocess.check_call([
    'twine',
    'register',
    full_filename,
])
#], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#common.git_clean_full()
