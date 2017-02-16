import setuptools

import sys
if not sys.version_info[0] == 3:
    sys.exit("Sorry, only python version 3 is supported")

setuptools.setup(
    name='pyawskit',
    version='0.1.25',
    description='pyawskit is a collection of utilities to help interact with aws',
    long_description='pyawskit helps you with various aws tasks',
    url='https://veltzer.github.io/pyawskit',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    keywords='aws utils',
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=[
        'boto3',  # used by ak_generate_ssh_config
        'pymount',  # used by ak_unify_disks
        'ujson',  # used by ak_generate_ssh_config
        'pypipegzip',  # used by ak_compress_s3_folder
    ],
    entry_points={
        'console_scripts': [
            'ak_prep_machine=pyawskit.ak_prep_machine:main',
            'ak_prep_account=pyawskit.ak_prep_account:main',
            'ak_generate_ssh_config=pyawskit.ak_generate_ssh_config:main',
            'ak_generate_etc_hosts=pyawskit.ak_generate_etc_hosts:main',
            'ak_generate_tilde_hosts=pyawskit.ak_generate_tilde_hosts:main',
            'ak_unify_disks=pyawskit.ak_unify_disks:main',
            'ak_show_disks=pyawskit.ak_show_disks:main',
            'ak_mount_disks=pyawskit.ak_mount_disks:main',
            'ak_compress_s3_folder=pyawskit.ak_compress_s3_folder:main',
            'ak_launch_machine=pyawskit.ak_launch_machine:main',
            'ak_copy_to_machine=pyawskit.ak_copy_to_machine:main',
        ],
    },
)
