#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from distutils.core import setup
from distutils.command.install import install
from distutils.dist import Distribution
from distutils.errors import DistutilsFileError
from distutils.util import subst_vars as distutils_subst_vars

readme = open('README.md').read()


class install_regate(install):

    def initialize_options(self):
        install.initialize_options(self)

    def finalize_options(self):
        install.finalize_options(self)

    def run(self):

        def subst_file(_file, vars_2_subst):
            input_file = os.path.join(self.build_lib, _file)
            output_file = input_file + '.tmp'
            subst_vars(input_file, output_file, vars_2_subst)
            os.unlink(input_file)
            self.move_file(output_file, input_file)

        inst = self.distribution.command_options.get('install')
        print inst
        vars_2_subst = {'PREFIX': inst['prefix'][1] if 'prefix' in inst else '',
                        'PREFIXDATA' : os.path.join(get_install_data_dir(inst), 'regate'),
                        }
        print os.path.join(get_install_data_dir(inst))
        for _file in self.distribution.fix_prefix:
            print _file
            subst_file(_file, vars_2_subst)
        _file = os.path.join('macsypy', '__init__.py')
        print _file
        subst_file(_file, {'VERSION' : self.distribution.get_version()})
        install.run(self)


class UsageDistribution(Distribution):

    def __init__(self, attrs = None):
        self.fix_prefix = None
        Distribution.__init__(self, attrs = attrs)


def get_install_data_dir(inst):

    if 'VIRTUAL_ENV' in os.environ:
        inst['prefix'] = ('environment', os.environ['VIRTUAL_ENV'])

    if 'install_data' in inst:
        install_dir = inst['install_data'][1]
    elif 'prefix' in inst:
        install_dir = os.path.join(inst['prefix'][1], 'share')
    else:
        install_dir = os.path.join('/', 'usr', 'share')
    return install_dir


def get_install_conf_dir(inst):
    if 'VIRTUAL_ENV' in os.environ:
        inst['prefix'] = ('environment', os.environ['VIRTUAL_ENV'])

    if 'install_conf' in inst:
        install_dir = inst['install_conf'][1]
    elif 'prefix' in inst:
        install_dir = os.path.join(inst['prefix'][1], 'etc')
    else:
        install_dir = '/etc'
    return install_dir


def get_install_doc_dir(inst):
    if 'VIRTUAL_ENV' in os.environ:
        inst['prefix'] = ('environment', os.environ['VIRTUAL_ENV'])

    if 'install_doc' in inst:
        install_dir = inst['install_doc'][1]
    elif 'prefix' in inst:
        install_dir = os.path.join(inst['prefix'][1], 'share', 'doc' )
    else:
        install_dir = os.path.join('/', 'usr', 'share', 'doc')
    return install_dir


def subst_vars(src, dst, vars):
    try:
        src_file = open(src, "r")
    except os.error as err:
        raise DistutilsFileError, "could not open '{0}': {1)".format(src, err)
    try:
        dest_file = open(dst, "w")
    except os.error as err:
        raise DistutilsFileError, "could not create '{0}': {1}".format(dst, err)
    with src_file:
        with dest_file:
            for line in src_file:
                new_line = distutils_subst_vars(line, vars)
                dest_file.write(new_line)



require_python = [ 'python (>=2.7, <3.0)' ]
require_packages = []

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
    data_files=[('share/regate', ['data/yaml_mapping.yaml', 'data/regate.ini', 'data/xmltemplate.tmpl'])],
    license="AFL",
    fix_prefix = ['bin/regate.py', 'bin/remag.py' ],
    cmdclass= {'install' : install_regate,

              },
    distclass = UsageDistribution
    )
