import setuptools

setuptools.setup(
    name='pyawskit',
    version='0.1.56',
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
        'sultan',  # for better ssh
        'pytconf',  # for command line parsing
    ],
    entry_points={
        'console_scripts': [
            'pyawskit = pyawskit.endpoints.main:main',
        ],
    },
)
