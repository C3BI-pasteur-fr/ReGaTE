ReGaTE
======

Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart

Welcome to ReGaTE's documentation! 
==================================
ReGaTE is a software component enabling the automated publication of Galaxy tools and workflows into the ELIXIR Tools and Data Services Registry (https://bio.tools).

This registry is a web portal for the exploration of bioinformatics resources, such as software packages, web services, websites, or reference databases. Through a dedicated interface, its users can search and locate relevant tools and data resources, and bioinformatics resource providers can enhance the visibility of their services. The registration of resources in the registry can be performed either manually, by filling a form on a web user interface, and providing the required description elements, or automatically by using the registry API.

ReGaTE uses the BioBlend API and the Registry API to completely automate the registration of the tools installed on any given Galaxy portal.
Central to the development of this tool is the mapping of the Galaxy datatype system to the EDAM Ontology. EDAM provides a controlled vocabulary for the description of scientific topics, software operations, types of data and data formats and it is used to describe the contents of the ELIXIR Registry. This mapping enables the automation of the registration of Galaxy tools by describing the format of their input and output data in the controlled vocabulary of the registry.

This mapping is being developed in collaboration with members of the Galaxy team, the EDAM ontology and the Common Workflow Language project.

`Olivia Doppelt-Azeroual, Fabien Mareuil, Eric Deveaud, Matus Kalas and Herve Menager`

Installation
============

.. toctree::
   :maxdepth: 2
   
   installation


Remag documentation
===================

.. toctree::
   :maxdepth: 2
   
   remag
   
   
Regate documentation
====================

.. toctree::
   :maxdepth: 2
   
   regate
   

Import documentation
====================

.. toctree::
   :maxdepth: 2
   
   import


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

