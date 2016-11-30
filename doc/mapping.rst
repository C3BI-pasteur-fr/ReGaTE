.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart

.. _mapping:


*******
Mapping
*******

The mapping from Galaxy datatypes to EDAM terms uses a mapping file which by default is `regate/data/yaml_mapping.yaml` in the regate package folder. You can customize this mapping to your convenience by creating a copy of this file and specifying its path in the `yaml_file` variable of the `regate_specific_section` section in the configuration file.

You can also use the `remag` tool, which generates a new mapping file. To generate this mapping, you need to have a local copy of the EDAM ontology OWL file (which can be downloaded from http://edamontology.org/EDAM.owl), and set the path to this local file in the `edam_file` variable of the `remag_specific_section` in the configuration file. The `yaml_file` variable of this same section is the path to the mapping file which is produced by remag. To run it, just type:

    remag --config_file regate.ini

