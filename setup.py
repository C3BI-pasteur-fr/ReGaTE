#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

from distutils.core import setup
from distutils.command.install import install
from distutils.dist import Distribution
from distutils.errors import DistutilsFileError
from distutils.util import subst_vars as distutils_subst_vars
from distutils.util import get_platform
from distutils.errors import DistutilsPlatformError

readme = open('README.md').read()

class install_regate(install):

    @property
    def skip_build(self):
        return self.skip_build

    @skip_build.setter
    def skip_build(self, x):
        self.skip_build = x


    def get_build_script(self):
        return os.path.join(self.build_base, 'scripts-{}'.format(self.config_vars['py_version_short']))

    def run(self):
        def subst_file(_file, vars_2_subst):
            input_file = os.path.join(self.get_build_script(), _file)
            output_file = input_file + '.tmp'
            subst_vars(input_file, output_file, vars_2_subst)
            os.unlink(input_file)
            self.move_file(output_file, input_file)

        #TODO : ask to bertrand why he is not a problem in his setup.py in the same section
        # Obviously have to build before we can substitute PREFIXDATA and after install without build
        if not self.skip_build:
            self.run_command('build')
            # If we built for any other platform, we can't install.
            build_plat = self.distribution.get_command_obj('build').plat_name
            # check warn_dir - it is a clue that the 'install' is happening
            # internally, and not to sys.path, so we don't check the platform
            # matches what we are running.
            if self.warn_dir and build_plat != get_platform():
                raise DistutilsPlatformError("Can't install when "
                                             "cross-compiling")
            self.skip_build = 1

        inst = self.distribution.command_options.get('install')
        vars_2_subst = {'PREFIXDATA': os.path.join(get_install_data_dir(inst), 'regate'),
                        }
        for _file in self.distribution.fix_prefix:
            subst_file(_file, vars_2_subst)
        install.run(self)

class UsageDistribution(Distribution):
    def __init__(self, attrs=None):
        self.fix_prefix = None
        Distribution.__init__(self, attrs=attrs)


def get_install_data_dir(inst):
    if 'VIRTUAL_ENV' in os.environ:
        inst['prefix'] = ('environment', os.environ['VIRTUAL_ENV'])

    if 'install_data' in inst:
        install_dir = inst['install_data'][1]
    elif 'prefix' in inst:
        install_dir = os.path.join(inst['prefix'][1], 'share')
    else:
        # TODO : /usr/share versus /usr/local/share?
        install_dir = os.path.join('/', 'usr', 'local', 'share')
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

setup(
    name='regate',
    version='0.9',
    description='Registration of Galaxy Tools in Elixir',
    long_description=readme,
    author='Olivia Doppelt-Azeroual and Fabien Mareuil',
    author_email='olivia.doppelt@pasteur.fr and fabien.mareuil@pasteur.fr',
    url='https://github.com/bioinfo-center-pasteur-fr/ReGaTE.git',
    scripts=[
        'bin/regate.py',
        'bin/remag.py'
    ],
    data_files=[('share/regate', ['data/yaml_mapping.yaml', 'data/regate.ini', 'data/xmltemplate.tmpl',
                                  'data/biotools.xsd'])],
    license="AFL",
    fix_prefix=['regate.py', 'remag.py'],
    cmdclass={'install': install_regate,
              },
    distclass=UsageDistribution
)
