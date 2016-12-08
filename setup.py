"""
A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import setuptools # for setup, find_packages

setuptools.setup(
    name='awskit',
    version='0.1.2',
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
    package_dir={'':'src'},
    packages=setuptools.find_packages('src'),
    install_requires=[
        'boto3', # used by ak_generate_ssh_config
        'mount', # used by ak_unify_disks
    ],
    entry_points={
        'console_scripts': [
            'ak_prep_machine=awskit.ak_prep_machine:main',
            'ak_generate_ssh_config=awskit.ak_generate_ssh_config:main',
            'ak_unify_disks=awskit.ak_unify_disks:main',
        ],
    },
)
