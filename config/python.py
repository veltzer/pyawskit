from typing import List


console_scripts: List[str] = [
    "pyawskit=pyawskit.main:main",
]
dev_requires: List[str] = [
    "pypitools",
]
config_requires: List[str] = [
    "pyclassifiers",
]
install_requires: List[str] = [
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
make_requires: List[str] = [
    "pymakehelper",
    "pydmt",
    "pyclassifiers",
    "types-tqdm",
]
test_requires: List[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "pyflakes",
    "flake8",
    "mypy",
    "types-requests",
]
requires = config_requires + install_requires + make_requires + test_requires
