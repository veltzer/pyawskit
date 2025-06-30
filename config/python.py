""" python deps for this project """

import config.shared

scripts: dict[str,str] = {
    "pyawskit": "pyawskit.main:main",
}
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
build_requires: list[str] = config.shared.PBUILD
test_requires: list[str] = config.shared.PTEST
types_requires: list[str] = [
    "types-tqdm",
    "types-requests",
]
requires = install_requires + build_requires + test_requires + types_requires
