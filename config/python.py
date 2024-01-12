from typing import List


console_scripts: List[str] = [
    "pyawskit=pyawskit.main:main",
]
dev_requires: List[str] = [
    "pymultigit",
    "pypitools",
    "black",
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
build_requires: List[str] = [
    "pymakehelper",
    "pydmt",
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
requires = config_requires + install_requires + build_requires + test_requires
