""" python deps for this project """

console_scripts: list[str] = [
    "pyawskit=pyawskit.main:main",
]
config_requires: list[str] = [
    "pyclassifiers",
]
install_requires: list[str] = [
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
build_requires: list[str] = [
    "pymakehelper",
    "pydmt",
    "types-tqdm",
]
test_requires: list[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "mypy",
    "types-requests",
]
requires = config_requires + install_requires + build_requires + test_requires
