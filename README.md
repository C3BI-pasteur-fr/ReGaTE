# ReGaTE
Registration of Galaxy Tools in Elixir


INSTALLATION
Do a virtualenv is better.

pip install -e git+https://github.com/bioinfo-center-pasteur-fr/ReGaTE.git#egg=regate

A src directory is created.

You can install dependencies with :

pip install -r src/regate/requirements.txt

To execute ReGaTE :

regate.py --galaxy_url a_galaxy_url --api_key the_galaxy_api_key --edam_file src/regate/yaml_mapping.yaml --tool_dir jsons_output



To execute ReMaG :

You can find the last version of EDAM here :
git clone https://github.com/edamontology/edamontology.git

file EDAM_X.owl

You can find a fork of galaxy with edam type here :
git clone https://github.com/galaxyproject/galaxy.git

You can find a mapping tsv file here :
git clone https://gist.github.com/0f559033430824f157fe.git

Execute remag with a recent Galaxy :
remag.py --galaxy_url a_galaxy_url --api_key the_galaxy_api_key --output_yaml myyaml.yaml --edam_file EDAM_X.owl

Execute remag with a tsv mapping file :
remag.py --mapping_file mapping --output_yaml myyaml.yaml --edam_file EDAM_X.owl

Execute remag with a datatype_conf with edam_type :
remag.py --datatype_conf --output_yaml myyaml.yaml --edam_file EDAM_X.owl 
