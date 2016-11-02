import subprocess # for check_call
import os.path # for expanduser

config_file=os.path.expanduser('~/.pypirc')

def git_clean_full():
    subprocess.check_call([
        'git',
        'clean',
        '-qffxd',
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
