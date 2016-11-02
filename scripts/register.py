#!/usr/bin/python3

'''
This script registers your project via twine.

It does:
- full clean
- build wheel using setup.py
- twine register
- full clean

References:
- https://packaging.python.org/distributing/
'''

import common # for git_clean_full

common.git_clean_full()
