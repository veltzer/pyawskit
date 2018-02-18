import setuptools

setuptools.setup(
    name='pyawskit',
    version='0.1.53',
    description='pyawskit is a collection of utilities to help interact with aws',
    long_description='pyawskit is a collection of utilities to help interact with aws',
    url='https://veltzer.github.io/pyawskit',
    download_url='https://github.com/veltzer/pyawskit',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    maintainer='Mark Veltzer',
    maintainer_email='mark.veltzer@gmail.com',
    license='MIT',
    platforms=['python3'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    keywords='aws utils python API command line',
    packages=setuptools.find_packages(),
    install_requires=[
        'pylogconf',  # for logging configuration
        'pyfakeuse',  # for coding
        'pypipegzip',  # used by pyawskit_compress_s3_folder
        'tqdm',  # used for progress
        'requests',  # for http
        'boto3',  # used by pyawskit_generate_ssh_config
        'pymount',  # used by pyawskit_unify_disks
        'ujson',  # used by pyawskit_generate_ssh_config
        'click',  # used for command line parsing
        'sultan',  # for better ssh
    ],
    entry_points={
        'console_scripts': [
            'pyawskit_prep_machine=pyawskit.scripts.prep_machine:main',
            'pyawskit_prep_account=pyawskit.scripts.prep_account:main',
            'pyawskit_generate_ssh_config=pyawskit.scripts.generate_ssh_config:main',
            'pyawskit_generate_etc_hosts=pyawskit.scripts.generate_etc_hosts:main',
            'pyawskit_generate_tilde_hosts=pyawskit.scripts.generate_tilde_hosts:main',
            'pyawskit_unify_disks=pyawskit.scripts.unify_disks:main',
            'pyawskit_show_disks=pyawskit.scripts.show_disks:main',
            'pyawskit_mount_disks=pyawskit.scripts.mount_disks:main',
            'pyawskit_compress_s3_folder=pyawskit.scripts.compress_s3_folder:main',
            'pyawskit_launch_machine=pyawskit.scripts.launch_machine:main',
            'pyawskit_copy_to_machine=pyawskit.scripts.copy_to_machine:main',
        ],
    },
)
