"""
A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import setuptools # for setup, find_packages

setuptools.setup(
    name='awskit',
    version='0.0.9',
    description='awskit is a collection of utilities to help interact with aws',
    long_description='this is the long description of awskit',
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
        'boto',
        'boto3',
    ],
    entry_points={
        'console_scripts': [
            'prep_machine=awskit.prep_machine:main',
        ],
    },
)
