import os.path
import shutil
import subprocess
import sys

import boto3
# noinspection PyPackageRequirements
import botocore
# noinspection PyPackageRequirements
import botocore.exceptions
from pypipegzip import pypipegzip


def copyfileobj(source, destination, buffer_size=1024 * 1024):
    """
    Copy a file from source to destination. source and destination
    must be file-like objects, i.e. any object with a read or
    write method, like for example StringIO.
    """
    while True:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        destination.write(copy_buffer)


def gzip_file(file_in: str, file_out: str) -> None:
    f_in = open(file_in, 'rb')
    f_out = pypipegzip.open(file_out, 'wb')
    shutil.copyfileobj(f_in, f_out)
    f_out.close()
    f_in.close()


def gzip_file_process(file_in: str, file_out: str) -> None:
    subprocess.check_call(
        'gzip < {file_in} > {file_out}'.format(
            file_in=file_in,
            file_out=file_out,
        ),
        shell=True,
    )


def object_exists(s3_connection, check_bucket_name: str, object_name: str) -> bool:
    """
    It seems funny we have to write this method but it seems that this
    is the way to check if an s3 bucket has an object.

    http://stackoverflow.com/questions/33842944/check-if-a-key-exists-in-a-bucket-in-s3-using-boto3

    :param s3_connection:
    :param check_bucket_name:
    :param object_name:
    :return: whether the object exists
    """
    try:
        s3_connection.Object(check_bucket_name, object_name).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise
    return True


def object_exists_bucket(bucket_obj, object_name: str) -> bool:
    """
    see the note above

    :param bucket_obj:
    :param object_name:
    :return: whether the object exists
    """
    try:
        bucket_obj.Object(object_name).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise
    return True


def catch_all(the_function):
    print('there')

    def new_function(*args, **kwargs):
        print('here')
        try:
            return the_function(*args, **kwargs)
        except Exception as e:
            print('got exception', e)
            sys.exit(1)
    return new_function


def process_one_file(basename, full_name, compressed_basename, full_compressed_name, bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    print('downloading', full_name, basename)
    bucket.download_file(full_name, basename)

    print('zipping', basename, compressed_basename)
    gzip_file_process(basename, compressed_basename)

    print('upload', compressed_basename, full_compressed_name)
    with open(compressed_basename, 'rb') as file_handle:
        new_object_summary = s3.ObjectSummary(bucket_name, full_compressed_name)
        new_object_summary.put(Body=file_handle)
        del new_object_summary

    print('removing', basename, compressed_basename)
    os.unlink(basename)
    os.unlink(compressed_basename)


def print_exception(e):
    print('exception happened', e)
    sys.exit(1)
