import setuptools


def get_readme():
    with open("README.rst") as f:
        return f.read()


setuptools.setup(
    # the first three fields are a must according to the documentation
    name="pyawskit",
    version="0.1.85",
    packages=[
        "pyawskit",
    ],
    # from here all is optional
    description="Pyawskit is your AWS Swiss Army Knife",
    long_description=get_readme(),
    long_description_content_type="text/x-rst",
    author="Mark Veltzer",
    author_email="mark.veltzer@gmail.com",
    maintainer="Mark Veltzer",
    maintainer_email="mark.veltzer@gmail.com",
    keywords=[
        "aws",
        "utils",
        "python",
        "API",
        "command",
        "line",
    ],
    url="https://veltzer.github.io/pyawskit",
    download_url="https://github.com/veltzer/pyawskit",
    license="MIT",
    platforms=[
        "python3",
    ],
    install_requires=[
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
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"console_scripts": [
        "pyawskit=pyawskit.main:main",
    ]},
)
