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

import subprocess

def git_clean_full():
    subprocess.check_call([
        'git',
        'clean',
        '-qffxd',
    ])

git_clean_full()
subprocess.check_call([
    'python3',
    'setup.py',
    'sdist',
])
'''
subprocess.check_call([
    'twine',
    'upload',
    'dist/*',
])
'''
