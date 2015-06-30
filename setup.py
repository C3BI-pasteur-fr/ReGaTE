#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

readme = open('README.md').read()


setup(
    name='regate',
    version='0.1',
    description='Registration of Galaxy Tools in Elixir',
    long_description=readme,
    author='Olivia Doppelt-Azeroual and Fabien Mareuil',
    author_email='olivia.doppelt@pasteur.fr',
    url='https://github.com/bioinfo-center-pasteur-fr/ReGaTE.git',
    scripts=[
        'bin/regate.py',
        'bin/remag.py',
        'bin/import2er.py'
    ],
    script_data={'data': ['yaml_mapping.yaml']},
    license="AFL"
    
)
