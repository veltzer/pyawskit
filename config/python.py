console_scripts = [
    "pyawskit=pyawskit.main:main",
]
dev_requires = [
    "pypitools",
]
config_requires = [
    "pyclassifiers",
]
install_requires = [
    "pylogconf",
    "pyfakeuse",
    "pypipegzip",
    "tqdm",
    "requests",
    "boto3",
    "pymount",
    "ujson",
    "sultan",
    "pytconf",
    "pyapikey",
    "furl",
    "docker-py",
]
make_requires = [
    "pymakehelper",
    "pydmt",
    "pyclassifiers",
    "types-tqdm",
]
test_requires = [
    "pylint",
    "pytest",
    "pytest-cov",
    "pyflakes",
    "flake8",
    "mypy",
    "types-requests",
]
requires = config_requires + install_requires + make_requires + test_requires
