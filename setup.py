#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os.path

SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, 'README.md')
readme = open(README).read()

setup(
    name='regate',
    version='0.10.0',
    description='Registration of Galaxy Tools in Elixir',
    long_description=readme,
    keywords=['GalaxyProject'],
    author='Olivia Doppelt-Azeroual and Fabien Mareuil',
    author_email='olivia.doppelt@pasteur.fr and fabien.mareuil@pasteur.fr',
    url='https://github.com/bioinfo-center-pasteur-fr/ReGaTE',
    packages=['regate'],
    install_requires=[
        'PyYAML',
        'html5lib==1.0b8',
        'rdflib',
        'cheetah',
        'requests',
        'configparser',
        'bioblend',
        'lxml'
    ],
    license="GPLv2",
    entry_points={
          'console_scripts': ['regate=regate.regate:run',
                              'remag=regate.remag:run'],
        },
    tests_require=['nose'],
    test_suite='nose.collector',
    include_package_data=True,
    zip_safe=False
)
