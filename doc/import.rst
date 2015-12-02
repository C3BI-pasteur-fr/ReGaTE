.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart
 
.. _import section:


***************************
Elixir Registry Importation
***************************


To create json and xml file and import the json files in the Elixir Registry you will need to set the pushtoelixir option to True in the config.ini file and specify your login on the registry and type:

"``regate.py --config_file config.ini``"

  
To only inmport already created json file in the registry set to True the options onlypush and pushtoelixir and specify your login and the directory where is tools (tool_dir) and type:
  
  "``regate.py --config_file config.ini``"
