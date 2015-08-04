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

"``remag.py -h``"
to see available options.
 
* The execution of remag creates an yaml file, which is the result of a mapping between galaxy extensions and edam format/data. 

To generate it:

-- With a mapping tsv file (first column: galaxy extension, second column the edam format: fomat_XXX, third column: description), type:

 "``remag.py --mapping_file mapping --output_yaml myyaml.yaml --edam_file EDAM_X.owl``"


-- With the Galaxe datatype_conf and edam_type attributes, type:

"``remag.py --datatype_conf yourdatatype --output_yaml myyaml.yaml --edam_file EDAM_X.owl``"

-- With a recent galaxy (https://github.com/galaxyproject/galaxy.git, it is necessary to use the dev branch for the moment. It is the only version where the edam format are available. You will need an account and an api key on this running galaxy to use remag), type:

"``remag.py --galaxy_url a_galaxy_url --api_key the_galaxy_api_key --output_yaml myyaml.yaml --edam_file EDAM_X.owl``"
