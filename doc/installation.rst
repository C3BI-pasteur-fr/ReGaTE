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
ReGaTE has five dependencies
 - Python modules *PyYAML* (>=3.11)
 - Python modules *rdflib* (>=4.2.0)
 - Python modules *requests* (>=2.7.0)
 - Python modules *cheetah* (>=2.4.4)
 - Python modules *configparser* (>=3.3.0.post2)
 - Python modules *bioblend* (>=0.5.4)
 - Python modules *lxml* (>=3.4.2)
 
These dependencies will automatically be installed during ReGaTE installation procedure.

**Python and Python-dev version 2.7** are required to run ReGaTE and ReMaG: https://docs.python.org/2.7/index.html
 

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

    git clone https://github.com/C3BI-pasteur-fr/ReGaTE.git
    cd ReGaTE
    python setup.py install

To install its dependencies::

    pip install -r requirements.txt


.. warning::
  if you update the version of ReGaTE, do not forget to uninstall the previous one! 

Uninstalling ReGaTE
========================

To uninstall ReGaTE (the last version installed), run::

    pip uninstall regate

