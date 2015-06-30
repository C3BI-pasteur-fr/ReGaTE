.. ReGaTE documentation master file, created by
   sphinx-quickstart on Mon Jun 29 16:39:40 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _installation:


************
Installation
************


ReGaTE dependencies
===================
ReGaTE has three dependencies
 - Python modules *PyYAML* (>=3.11)
 - Python modules *rdflib* (>=4.2.0)
 - And for the moment a particular version of bioblend (https://github.com/fmareuil/bioblend.git)
 
This dependencies will be installed during the installation procedure.
 
 **Python version 2.7** is required to run ReGaTE and ReMaG: https://docs.python.org/2.7/index.html
 

Installation procedure
======================
It is preferable to use virtualenv to avoid any conflict including bioblend conflict version.

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
  When installing a new version of ReGaTE, do not forget to uninstall the previous version installed ! 

Uninstalling ReGaTE
========================

To uninstall ReGaTE (the last version installed), run::

    pip uninstall regate

