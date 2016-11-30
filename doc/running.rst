.. ReGaTE Registration of Galaxy Tools in Elixir
 Authors: Olivia Doppelt-Azeroual, Fabien Mareuil
 ReGate is distributed under the terms of the GNU General Public License (GPLv2). 
 See the COPYING file for details.
 ReGaTE documentation master file, created by sphinx-quickstart

.. _running:


*******
Running
*******

Once you have set the regate configuration in regate.ini, you can run regate:

    regate --config_file regate.ini

The config_file parameter is the path of the configuration file you created. The regate tool runs for some time, and once the biotools files have been prepared and are ready for upload, you are asked to **enter your bio.tools password** (you will be asked again if authentication fails, e.g. if you type the wrong password). Upload errors are logged directly on your screen, but a more detailed log of the regate mapping and upload are stored in the ``activity.log`` file which is created in your working directory. 

The json files uploaded are also available in the folder corresponding to the tool_dir configuration variable.
