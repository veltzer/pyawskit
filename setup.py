"""
A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import setuptools

setuptools.setup(
    name='awskit',
    version='0.1.8',
    description='awskit is a collection of utilities to help interact with aws',
    long_description='awskit helps you with various aws tasks',
    url='https://veltzer.github.io/awskit',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    license='GPL3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='aws utils',
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=[
        'boto3',  # used by ak_generate_ssh_config
        'mount',  # used by ak_unify_disks
        'ujson',  # used by ak_generate_ssh_config
        'pipegzip',  # used by ak_compress_s3_folder
    ],
    entry_points={
        'console_scripts': [
            'ak_prep_machine=awskit.ak_prep_machine:main',
            'ak_generate_ssh_config=awskit.ak_generate_ssh_config:main',
            'ak_unify_disks=awskit.ak_unify_disks:main',
            'ak_compress_s3_folder=awskit.ak_compress_s3_folder:main',
            'ak_launch_machine=awskit.ak_launch_machine:main',
        ],
    },
)
