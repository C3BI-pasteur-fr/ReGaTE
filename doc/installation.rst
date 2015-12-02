.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart

.. _installation:


************
Installation
************


ReGaTE dependencies
===================
ReGaTE has three dependencies
 - Python modules *PyYAML* (>=3.11)
 - Python modules *rdflib* (>=4.2.0)
 - A fork of BioBlend (https://github.com/galaxyproject/bioblend) available at (https://github.com/fmareuil/bioblend.git)
 
These dependencies will automatically be installed during ReGaTE installation procedure.

**Python version 2.7** is required to run ReGaTE and ReMaG: https://docs.python.org/2.7/index.html
 

Installation procedure
======================
We recommend to use a virtualenv in order to avoid conflicts with your LINUX configuration (as well as with BioBlend main version).

First install virtualenv::

    pip install virtualenv

Then, create a virtual environnement::

    virtualenv ReGaTE_env
And, activate it:: 

    cd ReGaTE_env
    source bin/activate

To install ReGaTE::

    git clone https://github.com/bioinfo-center-pasteur-fr/ReGaTE.git
    cd ReGaTE
    python setup.py install

To install its dependencies::

    pip install -r src/regate/requirements.txt


.. warning::
  if you update the version of ReGaTE, do not forget to uninstall the previous one! 

Uninstalling ReGaTE
========================

To uninstall ReGaTE (the last version installed), run::

    pip uninstall regate

