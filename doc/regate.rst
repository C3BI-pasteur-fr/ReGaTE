.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart

.. _regate guide:


************
ReGaTE Guide
************


In order to run ReGaTE (Registration of Galaxy Tools in Elixir) you need an account on a galaxy workbench and a generated API Key (see galaxy documentation if necessary https://wiki.galaxyproject.org/Learn/API).

* to see available options.

Type:

"``regate.py -h``"

* to generate a template of the config.ini file type:
"``regate.py --templateconfig``"
A regate.ini file will be created


* to generate a list of json files corresponding to the description of each tool installed in your galaxy from any toolshed.

Type:

"``regate.py --config_file regate.ini``"

You will need to define the galaxy server url usable with the api (galaxy_url_api) and the galaxy server usable with a web browser (it can be the same), the api_key of an galaxy account, a contact name, a contact email and a ressource name, and a name for the output directory.
For each Galaxy server available tool a xml and a json description file will be created.


yaml_file option is a mapping file between the EDAM ontology and the galaxy extensions in a yaml format.
By default a yaml file obtain from the Edam ontology version 1.11 is used in regate. To use an other yaml file you can specify the yaml_file option.

**To update the yaml file, use the program remag.py** see :ref:`remag options section <remag guide>`.

**To import json in the Elixir Registry** see :ref:`import section <import section>`.

