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
 - And for the moment a specific version of bioblend (https://github.com/fmareuil/bioblend.git)
 
These dependencies will be automatically installed during the installation procedure.
 
 **Python version 2.7** is required to run ReGaTE and ReMaG: https://docs.python.org/2.7/index.html
 

Installation procedure
======================
It is better to use virtualenv to avoid any conflict (including bioblend version conflict).

First install virtualenv::

    pip install virtualenv

Create a virtual environnement::

    virtualenv ReGaTE_env
    cd ReGaTE_env
    source bin/activate

To install regate::

    pip install -e git+https://github.com/bioinfo-center-pasteur-fr/ReGaTE.git#egg=regate

To install dependencies::

    pip install -r src/regate/requirements.txt


.. warning::
  When installing a new version of ReGaTE, do not forget to uninstall the previous version! 

Uninstalling ReGaTE
========================

To uninstall ReGaTE (the last version installed), run::

    pip uninstall regate

