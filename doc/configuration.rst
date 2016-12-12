.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart

.. _configuration:


*************
Configuration
*************


In order to run ReGaTE you need an account on the http://bio.tools server and on the galaxy server that you want to register.

* Register (if you haven't done it yet) on http://bio.tools by clicking on "Sign up" on the http://bio.tools server

* Generate the regate.ini configuration file by typing

    regate --templateconfig

* Edit the regate.ini configuration file which was created in your working directory. The different variables to edit are **all** documented in the file itself. The ones that you **must** set are:

  - `galaxy_url_api` and `galaxy_url`, which should be set to the URL of the Galaxy server you aim at publishing in bio.tools. `galaxy_url` will be the base of the URL use to link from bio.tools to your Galaxy server, whereas `galaxy_url_api` will be used as the Galaxy API endpoint to query the server.
  
  - `api_key` is the API key for your user on the server. Please remember this key is **absolutely** private, meaning that your configuration file cannot be distributed.
  
  - `contactName` and `contactEmail` will be used as contact information for all the Galaxy tools registered for your server.
  
  - `resourceName` is the name of the bio.tools collection that will group all the Galaxy tools from your server. Only these tools should be registered with this collection.
  
  - In the `[regate_specific_section]`, `login` is your login on the bio.tools server.
