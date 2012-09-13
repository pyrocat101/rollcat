#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
        name="rollcat",
        version="0.1.0",
        description="Rainbows and unicorns!",
        long_description="rollcat is a self-contained Python port of lolcat",
        author="metaphysiks",
        author_email="i@dingstyle.me",
        keywords=("cat", "rainbow"),
        package_dir={'rollcat': 'src'},
        packages=['rollcat'],
        entry_points={
            'console_scripts': ['rollcat = rollcat.cat:main'],
        }
    )
