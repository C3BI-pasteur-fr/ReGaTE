ReGaTE documentation
********************

ReGaTE is a command line utility to automate the publication of Galaxy_ tools into the ELIXIR bio.tools_ registry.

bio.tools_ is a web portal for the exploration of bioinformatics resources, such as software packages, web services, websites, or reference databases. Through a dedicated interface, its users can search and locate relevant tools and data resources, and bioinformatics resource providers can enhance the visibility of their services. The registration of resources in the registry can be performed either manually, by filling a form on a web user interface, and providing the required description elements, or automatically by using the bio.tools `bio.tools API`_.

ReGaTE uses the BioBlend_ API and the bio.tools API to completely automate the registration of the tools installed on any given Galaxy portal.
Central to the development of this tool is the mapping of the Galaxy datatype system to the EDAM_ Ontology. EDAM provides a controlled vocabulary for the description of scientific topics, software operations, types of data and data formats and it is used to describe the contents of bio.tools. This mapping enables the automation of the registration of Galaxy tools by describing the format of their input and output data in the controlled vocabulary of the registry.

.. toctree::
   :maxdepth: 2
   
   installation
   
   configuration
   
   running
   
   mapping

.. _bio.tools: https://bio.tools
.. _bio.tools API: http://biotools.readthedocs.io/en/latest/api_reference.html
.. _Galaxy: http://galaxyproject.org
.. _EDAM: http://edamontology.org
.. _BioBlend: https://bioblend.readthedocs.io

