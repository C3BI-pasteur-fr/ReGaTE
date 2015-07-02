.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart
   
.. _regate guide:


************
ReGaTE Guide
************


In order to run ReGaTE you need an account on a galaxy workbench with an API Key (see galaxy documentation if necessary https://wiki.galaxyproject.org/Learn/API).

* Type:

  "``regate.py -h``"
  to see available options.

* Type:

  "``regate.py --galaxy_url your_galaxy_url --api_key your_galaxy_api_key --edam_file src/regate/data/yaml_mapping.yaml --tool_dir jsons_output``"
  
  to obtain a list of json files which are the description of each tool installed in your galaxy from a toolshed.
  
  yaml_mapping.yaml is a mapping file between the EDAM ontology and the galaxy extension in a yaml format. You can generate a new version of this file with remag.py see :ref:`remag options section <remag guide>`.
  
**To import json in the Elixir Registry see** :ref:`import section <import section>`.
