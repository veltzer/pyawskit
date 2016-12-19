"""
This module enables working with gunzip to open gzip files

The reason for this module is the following benchmark:
- with python gzip decoded to text:
$ time ./flipkart_read_all_clickstream.py
real    4m23.271s
user    55m55.884s
sys     1m28.552s
- with pipe from zcat:
$ time ./flipkart_read_all_clickstream.py
real    3m13.042s
user    32m49.568s
sys     4m0.020s
- with pipe from zcat + decoding:
$ time ./flipkart_read_all_clickstream.py
real    3m19.863s
user    32m2.292s
sys     4m17.796s
"""

import subprocess
import io
import gzip


# noinspection PyShadowingBuiltins
def open(filename: str, mode="rb", use_process=True, encoding=None):
    if "r" in mode:
        if use_process:
            args = [
                "/bin/zcat",
                filename,
            ]
            process = subprocess.Popen(args, stdout=subprocess.PIPE)
            if "b" in mode:
                return process.stdout
            if "t" in mode:
                stdout = io.TextIOWrapper(process.stdout, encoding=encoding)
                return stdout
            raise ValueError("please specify t or b in mode")
        else:
            return gzip.open(filename, encoding=encoding, mode=mode)
    if "w" in mode:
        return gzip.open(filename, encoding=encoding, mode=mode)
