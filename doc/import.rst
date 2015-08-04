.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart
 
.. _import section:


***************************
Elixir Registry Importation
***************************


Currently there are two ways to import a json file in the Elixir Registry:

* with the command import2er.py

  "``import2er.py -h``"
  to see available options.
  
  "``import2er.py --login your_registry_login --json_dir directory_with_json_file``"
  
  to import all json files of the directory in the registry

* directly with regate

  "``regate.py --galaxy_url your_galaxy_url --api_key your_galaxy_api_key --edam_file src/regate/data/yaml_mapping.yaml --tool_dir jsons_output --pushtoelixir --login your_registry_login``"
  
  to create json files and import them in the registry directly after
  
  "``regate.py --pushtoelixir --onlypush --login your_registry_login --tool_dir json_directory``"
  
  to only import json files in the registry
