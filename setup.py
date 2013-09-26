#!/usr/bin/env python

from setuptools import setup, find_packages

version = "0.2.0"

setup(
    name="rollcat",
    version=version,
    description="Rainbows and unicorns!",
    long_description="rollcat is a Python port of lolcat.",
    author="Linjie Ding",
    author_email="i@pyroc.at",
    keywords=("cat", "rainbow"),
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    license="MIT",
    url="https://github.com/pyrocat101/rollcat/",
    install_requires=["docopt>=0.6.1", "schema>=0.2.0"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console"
    ],
    entry_points={
        "console_scripts": [
            "rollcat = rollcat:entry"
        ]
    }
)
