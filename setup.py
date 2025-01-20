#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='common_widgets',
    version='0.0.1',
    description='Common Widgets',
    packages=find_packages("src"),
    package_dir={'': 'src'},
    install_requires=[

    ],
    extras_require={
        'dev': [
        ],
    },
    zip_safe=True
)
