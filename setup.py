#!/usr/bin/env python
# -*- coding: utf-8 -*-

import versioneer

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'cameo>=0.5.0',
    'swiglpk>=1.2.14',
    'lxml',
    'python-libsbml'
]

test_requirements = [
    # TODO: put package test requirements here
    'nose>=1.3.7'
]

setup(
    name='memote',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Test suite for genome -scale metabolic models",
    long_description=readme,
    author="Christian Lieven",
    author_email='clie@biosustain.dtu.dk',
    url='https://github.com/ChristianLieven/memote',
    packages=[
        'memote',
    ],
    package_dir={'memote':
                 'memote'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='memote',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
