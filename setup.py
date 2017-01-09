"""
A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import setuptools

setuptools.setup(
    name='pyawskit',
    version='0.1.12',
    description='pyawskit is a collection of utilities to help interact with aws',
    long_description='pyawskit helps you with various aws tasks',
    url='https://veltzer.github.io/pyawskit',
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
        'pymount',  # used by ak_unify_disks
        'ujson',  # used by ak_generate_ssh_config
        'pypipegzip',  # used by ak_compress_s3_folder
    ],
    entry_points={
        'console_scripts': [
            'ak_prep_machine=pyawskit.ak_prep_machine:main',
            'ak_generate_ssh_config=pyawskit.ak_generate_ssh_config:main',
            'ak_unify_disks=pyawskit.ak_unify_disks:main',
            'ak_compress_s3_folder=pyawskit.ak_compress_s3_folder:main',
            'ak_launch_machine=pyawskit.ak_launch_machine:main',
        ],
    },
)
