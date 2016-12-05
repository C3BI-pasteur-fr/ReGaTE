ReGaTE README file
==================

ReGaTE is a command line utility that automates the registration of the tools installed on any given Galaxy portal in ELIXIR bio.tools.

The full documentation is available on http://regate.readthedocs.io, including detailed setup and configuration instructions. However, a quick setup and run of ReGaTE is as easy as:

```bash
pip install git+https://github.com/C3BI-pasteur-fr/ReGaTE.git
regate --templateconfig
vim regate.ini #here fill in the configuration variables sensibly before running regate
regate --config_file regate.ini
```
