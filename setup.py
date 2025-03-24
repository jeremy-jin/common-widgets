#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='common_widgets',
    version='0.0.2',
    description='Common Widgets',
    packages=find_packages("src"),
    package_dir={'': 'src'},
    install_requires=[

    ],
    extras_require={
        'dev': [
            "black==25.1.0"
        ],
    },
    zip_safe=True
)
