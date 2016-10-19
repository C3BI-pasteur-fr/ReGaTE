.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart

.. _remag guide:


***********
ReMaG Guide
***********


In order to run ReMaG (Registry Mapping Galaxy) you need the EDAM ontology file in the owl format https://github.com/edamontology/edamontology.git, EDAM_X.owl file.

* Type:

"``remag -h``"
to see available options.
 
* The execution of remag creates an yaml file, which is the result of a mapping between galaxy extensions and edam format/data. 

To generate it:

-- With a recent galaxy (https://github.com/galaxyproject/galaxy.git, You will need an account and an api key on this running galaxy to use remag), type:

"``remag --config_file config.ini``"

* You can obtain a template of the config.ini file with the command:

"``remag --templateconfig``"

A regate.ini file will be created, you will need to specify the galaxy server url usable with the api (galaxy_url_api), the api_key of an galaxy account, the edam ontology file, and a name for the output yaml file (output_yaml)
