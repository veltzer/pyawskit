import subprocess # for check_call
import os.path # for expanduser
import sys # for exit

config_file=os.path.expanduser('~/.pypirc')

def check_call_no_output(args):
    p = subprocess.Popen(
            args,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
    )
    (res_stdout, res_stderr) = p.communicate()
    if p.returncode:
        print(res_stdout, end='')
        print(res_stderr, end='')
        sys.exit(p.returncode)

def git_clean_full():
    check_call_no_output([
        'git',
        'clean',
        '-qffxd',
    ])
