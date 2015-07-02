.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart
   
.. _remag guide:


***********
ReMaG Guide
***********


In order to run ReMaG you need a description file of the EDAM ontology in the owl format https://github.com/edamontology/edamontology.git, EDAM_X.owl file.

* Type:

  "``remag.py -h``"
  to see available options.
  
* The execution of remag creates an yaml file, which is the result of a mapping between galaxy extension and edam format/data. To obtain it:

-- With a mapping tsv file (first column: galaxy extension, second column the edam format: fomat_XXX, third column: description), type:

  "``remag.py --mapping_file mapping --output_yaml myyaml.yaml --edam_file EDAM_X.owl``"


-- With a datatype_conf with edam_type attribut, type:

  "``remag.py --datatype_conf yourdatatype --output_yaml myyaml.yaml --edam_file EDAM_X.owl``"

-- With a recent galaxy (https://github.com/galaxyproject/galaxy.git, for the moment the dev branch is necessary to have the edam format, you need an account and an api key on this galaxy), type:

  "``remag.py --galaxy_url a_galaxy_url --api_key the_galaxy_api_key --output_yaml myyaml.yaml --edam_file EDAM_X.owl``"
  
 
  
