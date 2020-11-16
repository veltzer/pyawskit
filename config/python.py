import config.project

package_name = config.project.project_name

console_scripts = [
    'pyawskit=pyawskit.main:main',
]

setup_requires = [
]

run_requires = [
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
]

test_requires = [
    'pylint',  # to check for lint errors
    'pytest',  # for testing
    'pyflakes',  # for testing
]

dev_requires = [
    'pyclassifiers',  # for programmatic classifiers
    'pypitools',  # for upload etc
    'pydmt',  # for building
    'Sphinx',  # for the sphinx builder
]

install_requires = list(setup_requires)
install_requires.extend(run_requires)

python_requires = ">=3.6"

extras_require = {
    #    ':python_version == "2.7"': ['futures'],  # for python2.7 backport of concurrent.futures
}
