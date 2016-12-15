#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct. 23, 2014

@author: Olivia Doppelt-Azeroual, CIB-C3BI, Institut Pasteur, Paris
@author: Fabien Mareuil, CIB-C3BI, Institut Pasteur, Paris
@author: Hervé Ménager, CIB-C3BI, Institut Pasteur, Paris
@contact: olivia.doppelt@pasteur.fr
@project: ReGaTE
@githuborganization: C3BI-pasteur-fr
"""

import sys
import re
import os
import glob
import shutil
import string
import argparse
import json
import yaml
import requests
import getpass
import copy
import logging
import configparser
import collections

from lxml import etree
from Cheetah.Template import Template
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy import GalaxyInstance

from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

# first logger
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# second logger
file_handler_edam = RotatingFileHandler('edam_mapping.log', 'a', 1000000, 1)

file_handler_edam.setLevel(logging.WARNING)
file_handler_edam.setFormatter(formatter)
logger.addHandler(file_handler_edam)

DEFAULT_EDAM_DATA = {
    "term": "Data",
    "uri": "http://edamontology.org/data_0006"
}
DEFAULT_EDAM_FORMAT = {
    "term": "Textual format",
    "uri": "http://edamontology.org/format_2330"
}
DEFAULT_EDAM_OPERATION = {
    "uri": "http://edamontology.org/operation_0004",
    "term": "Operation"
}
DEFAULT_EDAM_TOPIC = {
    "uri": "http://edamontology.org/topic_0003",
    "term": "Topic"
}

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data_path(path):
    return os.path.join(_ROOT, 'data', path)


class Config(object):

    """
    class config to parse and check the config.ini file
    """

    def __init__(self, configfile, script):
        self.conf = config_parser(configfile)
        self.galaxy_url_api = self.assign("galaxy_server", "galaxy_url_api", ismandatory=True)
        self.api_key = self.assign("galaxy_server", "api_key", ismandatory=True)
        if script == "regate":
            self.galaxy_url = self.assign("galaxy_server", "galaxy_url", ismandatory=True)
            self.tools_default = self.assign("galaxy_server", "tools_default", ismandatory=True)
            self.contactName = self.assign("galaxy_server", "contactName", ismandatory=True)
            self.contactEmail = self.assign("galaxy_server", "contactEmail", ismandatory=True)
            self.resourcename = self.assign("galaxy_server", "resourcename", ismandatory=True)
            self.onlypush = self.assign("regate_specific_section", "onlypush", ismandatory=False, boolean=True)
            self.prefix_toolname = self.assign("regate_specific_section", "prefix_toolname", ismandatory=False)
            self.suffix_toolname = self.assign("regate_specific_section", "suffix_toolname", ismandatory=False)

            if self.onlypush:
                self.pushtoelixir = self.assign("regate_specific_section", "pushtoelixir", ismandatory=True,
                                                message="pushtoelixir option is mandatory if onlypush is True",
                                                boolean=True)
                if not self.pushtoelixir:
                    raise KeyError("pushtoelixir option must be True if onlypush is True")

            else:
                self.pushtoelixir = self.assign("regate_specific_section", "pushtoelixir", ismandatory=False,
                                                boolean=True)
            if self.pushtoelixir:
                self.login = self.assign("regate_specific_section", "login", ismandatory=True,
                                         message="login option is mandatory if pushtoelixir is True")
                self.host = self.assign("regate_specific_section", "bioregistry_host", ismandatory=True,
                                        message="bioregistry_host option is mandatory if pushtoelixir is True")
                self.ssl_verify = self.assign("regate_specific_section", "ssl_verify", ismandatory=True,
                                              message="ssl_verify option is mandatory if pushtoelixir is True",
                                              boolean=True)
                self.accessibility = self.assign("regate_specific_section", "accessibility", ismandatory=True,
                                                 message="accessibility option is mandatory if pushtoelixir is True")
            else:
                self.login = self.assign("regate_specific_section", "login", ismandatory=False)
                self.host = self.assign("regate_specific_section", "bioregistry_host", ismandatory=False)
                self.ssl_verify = self.assign("regate_specific_section", "ssl_verify", ismandatory=False, boolean=True)
            self.accessibility = self.assign("regate_specific_section", "accessibility", ismandatory=True)
            self.tool_dir = self.assign("regate_specific_section", "tool_dir", ismandatory=True)
            self.yaml_file = self.assign("regate_specific_section", "yaml_file", ismandatory=False)
            self.xmltemplate = self.assign("regate_specific_section", "xmltemplate", ismandatory=False)
            self.xsdbiotools = self.assign("regate_specific_section", "xsdbiotools", ismandatory=False)
        if script == "remag":
            self.edam_file = self.assign("remag_specific_section", "edam_file", ismandatory=True)
            self.output_yaml = self.assign("remag_specific_section", "output_yaml", ismandatory=True)

    def assign(self, section, key, ismandatory=True, message=None, boolean=False):
        """
            return value if key exists in config.ini file or an error or None if not, depending on whether the option
            is mandatory or not
        """
        if ismandatory:
            if self.exist(section, key):
                return self.getvalue(section, key, boolean=boolean)
            else:
                if message:
                    raise KeyError(message)
                else:
                    raise KeyError("{0} option is mandatory".format(key))
        if not ismandatory:
            if self.exist(section, key):
                return self.getvalue(section, key, boolean=boolean)
            else:
                return None

    def getvalue(self, section, key, boolean=False):
        """
            test if key is a boolean and return value
        """
        if boolean:
            return self.conf.getboolean(section, key)
        else:
            return self.conf.get(section, key)

    def exist(self, section, key):
        """
            Check if key exist in the section
        """
        if key in self.conf[section] and self.conf.get(section, key):
            return True
        else:
            return False


def build_tool_name(tool_id, prefix, suffix):
    """
    @tool_id: tool_id
    builds the tool_name with the tool id, its version
    and the prefix/suffix defined in the config file
    """
    try:
        tool_name = string.split(tool_id, '/')[-2]
    except IndexError:
        tool_name = tool_id
    tool_name = re.sub('[^0-9a-zA-Z\_\-\.\~]', '-', tool_name)
    if prefix:
        name = str(prefix) + '-' + tool_name
    else:
        name = tool_name
    if suffix:
        name = name + '-' + str(suffix)
    return name


def get_source_registry(tool_id):
    """
    :param tool_id:
    :return:
    """
    try:
        source_registry = "/".join(tool_id.replace('repos', 'view', 1).split('/')[0:-2])
        return "https://" + source_registry
    except ValueError:
        logger.warning("ValueError:", tool_id)
        return ""


def build_filename(tool_id, version):
    try:
        try:
            source = string.split(tool_id, '/')[-2]
        except IndexError:
            source = tool_id
        return source + "_" + version
    except ValueError:
        logger.warning("ValueError:", tool_id)
        return ""


def format_description(description):
    """
    Test the first and last char of a description and replace them
    with the format adapted to Elixir
    """
    try:
        size = len(description)
        if description[size - 1] == '.':
            return description[0].upper() + description[1:size]
        else:
            return description[0].upper() + description[1:size] + '.'
    except IndexError:
        logger.warning(description)


def detect_toolid_duplicate(tool_list):
    id_list = list()
    for tool in tool_list:
        id_list.append(build_filename(tool[u'id'], tool[u'version']))

    duplicate_tools = [item for item, count in collections.Counter(id_list).items() if count > 1]
    if duplicate_tools:
        for dup in duplicate_tools:
            logger.warning("The tool {0} is present multiple times on this instance with the same version.".format(dup))


def edam_to_uri(edam, element):
    """
    :param edam:
    :returns edam uri from an edam term:
    """
    try:
        uri = re.split("_|:", edam)
        if len(uri) == 2:
            uri = "http://edamontology.org/{}_{:0>4d}".format(uri[0], int(uri[1]))
        else:
            uri = "http://edamontology.org/{}_{:0>4d}".format(uri[1], int(uri[2]))
    except TypeError:
        if element == 'data':
            uri = "http://edamontology.org/data_0006"
        else:
            uri = "http://edamontology.org/format_1915"
        logger.warning("EDAM MAPPING: TERM ----{0}---- is missing from EDAM current version".format(edam))
    return uri


def find_edam_format(format_name, mapping_edam):
    """
    :param format_name:
    :param mapping_edam:
    :return: edam format from a format (extension) in galaxy
    """
    if format_name in mapping_edam:
        edam_format = mapping_edam[format_name]['formats'][0]
    else:
        edam_format = DEFAULT_EDAM_FORMAT
    return edam_format


def find_edam_data(format_name, mapping_edam):
    """
    :param format_name:
    :param mapping_edam:
    :return edam data of a defined format_name:
    """
    if format_name in mapping_edam:
        edam_data = mapping_edam[format_name]['data'][0]
    else:
        edam_data = DEFAULT_EDAM_DATA
    return edam_data


def build_general_dict(tool_meta_data, conf):
    """
    Extract informations from a galaxy json tool and return the general json in the biotools format
    :param tool_meta_data: galaxy json tool
    :conf : regate.ini config file
    :return: biotools dictionary
    :rtype: dictionary
    """
    if tool_meta_data[u'description'] != '':
        description = format_description(tool_meta_data[u'description'])
    else:
        description = 'Galaxy tool {0}.'.format(tool_meta_data[u'description'])
    gen_dict = {
        'version': tool_meta_data[u'version'],
        'versionID': tool_meta_data[u'version'],
        'description': description,
        'uses': [{
            "usesName": 'Toolshed entry for "' + tool_meta_data[u'id'] + '"',
            "usesHomepage": 'http://' + requests.utils.quote(tool_meta_data[u'id']),
            "usesVersion": tool_meta_data[u'version']
        }],
        'collection': [conf.resourcename],
        # we need to find a 50 chars or less string for sourceRegistry
        # u'sourceRegistry': get_source_registry(tool_meta_data[u'id']),
        'resourceType': ["Tool"],
        'maturity': 'Mature',
        'platform': ['Linux'],
        'interface': [{
            'interfaceType': "Web UI",
            'interfaceDocs': '',
            'interfaceSpecURL': '',
            'interfaceSpecFormat': ''
        }],
        'topic': [DEFAULT_EDAM_TOPIC],
        'publications': {u'publicationsPrimaryID': "None", 'publicationsOtherID': []},
        'homepage': "{0}?tool_id={1}".format(conf.galaxy_url + '/tool_runner',
                                             requests.utils.quote(tool_meta_data[u'id'])),
        'accessibility': [conf.accessibility],
        'mirror': [],
        'canonicalID': '',
        'tag': [],
        'elixirInfo': {
            'elixirStatus': '',
            'elixirNode': ''
        },
        'language': [],
        'license': '',
        'cost': '',
        'docs': {
            'docsHome': '',
            'docsTermsOfUse': '',
            'docsDownload': '',
            'docsCitationInstructions': ''
        },
        'credits': {
            'creditsDeveloper': [],
            'creditsContributor': [],
            'creditsInstitution': [],
            'creditsInfrastructure': [],
            'creditsFunding': []
        },
        'contact': [{
            'contactEmail': conf.contactEmail,
            'contactURL': '',
            'contactName': conf.contactName,
            'contactTel': '',
            'contactRole': []
        }],
        'toolType': ['Web application']
    }
    return gen_dict


def build_function_dict(json_tool, mapping_edam):
    """
    Extract information from a galaxy json tool and return a list of functions in the json biotools format
    :param json_tool: galaxy json tool
    :return: list of functions in the json biotools format
    :rtype: list
    """
    list_func = []

    listinps = inputs_extract(json_tool['inputs'], mapping_edam)

    listoutps = outputs_extract(json_tool['outputs'], mapping_edam, listinps)
    func_dict = {
        'functionDescription': json_tool['description'],
        'operation': [DEFAULT_EDAM_OPERATION],
        'output': listoutps,
        'input': listinps,
        'functionHandle': "functionHandle"
    }
    list_func.append(func_dict)
    return list_func


def inputs_extract(inputs_json, mapping_edam):
    """
    Extract type data param of a galaxy json tool inputs and return a list of dictionary in the json biotools format
    :param inputs_json: inputs part of a json tool
    :return: list of dictionary in the json biotools format
    :rtype: list
    """

    def inputs_extract_data(data_json):
        """
        Save param type data from a json tool galaxy in a list
        :param data_json:
        :return: None
        """
        data_types = [find_edam_data(extension, mapping_edam) for extension in data_json["extensions"]]
        data_formats = [find_edam_format(extension, mapping_edam) for extension in data_json["extensions"]]
        if len(data_types) == 1:
            data_item = {'dataType': data_types[0],
                         'dataFormat': data_formats,
                         'dataHandle': data_json['name'],
                         'dataDescription': data_json['label']
                         }
        else:
            data_item = {'dataType': DEFAULT_EDAM_DATA,
                         'dataFormat': data_formats,
                         'dataHandle': data_json['name'],
                         'dataDescription': data_json['label']
                         }
        listdata.append(data_item)

    def inputs_extract_repeat(repeat_json):
        """
        Recursive function in order to explore repeat param of a galaxy json tool
        :param repeat_json: Repeat param part of a galaxy json tool
        :return: None
        """
        for dictinprep in repeat_json['inputs']:
            if dictinprep['type'] == "conditional":
                inputs_extract_conditional(dictinprep)
            elif dictinprep['type'] == "repeat":
                inputs_extract_repeat(dictinprep)
            elif dictinprep["type"] in ["data", "datacollection"]:
                inputs_extract_data(dictinprep)

    def inputs_extract_conditional(conditional_json):
        """
        Recursive function in order to explore conditional param of a galaxy json tool
        :param conditional_json: conditional param part of a galaxy json tool
        :return: None
        """
        for case in conditional_json["cases"]:
            for dictinpcond in case["inputs"]:
                if dictinpcond['type'] == "conditional":
                    inputs_extract_conditional(dictinpcond)
                elif dictinpcond['type'] == "repeat":
                    inputs_extract_repeat(dictinpcond)
                elif dictinpcond["type"] in ["data", "datacollection"]:
                    inputs_extract_data(dictinpcond)

    listdata = list()
    for dictinp in inputs_json:
        if dictinp['type'] == "conditional":
            inputs_extract_conditional(dictinp)
        elif dictinp['type'] == "repeat":
            inputs_extract_repeat(dictinp)
        elif dictinp["type"] in ["data", "datacollection"]:
            inputs_extract_data(dictinp)
    # if any([len(data['dataType'])==0 or len(data['dataFormat'])==0 for data in listdata]):
    #    logger.warning("data/formats mapping not found for inputs_json:" + str(inputs_json))
    return listdata


def outputs_extract(outputs_json, mapping_edam, biotools_inputs):
    """
    Extract type output param of a galaxy json tool outputs and return a list of dictionary in the json biotools format
    :param outputs_json: output param of a galaxy json tool outputs
    :return: list of dictionary in the json biotools format
    :rtype: dictionary
    """
    listoutput = list()
    for output in outputs_json:
        if output['format'] != 'input':
            try:
                outputdict = {'dataType': find_edam_data(output[u'format'], mapping_edam),
                              'dataFormat': [find_edam_format(output[u'format'], mapping_edam)],
                              'dataHandle': output['format'], 'dataDescription': output['name']
                              }
            except KeyError:
                    logger.warning(
                        "EDAM MAPPING: TERM ----{0}---- is missing from EDAM current version".format(output[u'format']))
        else:
            # FIXME: copying the datatype/format from the source would work if only the Galaxy API used
            # by bioblend sent the format_source information
            # biotools_input_source = [biotools_input for biotools_input in biotools_inputs if biotools_input['dataHandle']==output['format_source']][0]
            # outputdict = {'dataType': biotools_input_source['dataType'],
            #         'dataFormat': biotools_input_source['dataFormat'],
            #         'dataHandle': output['format'], 'dataDescription': output['name']
            #          }
            outputdict = {'dataType': DEFAULT_EDAM_DATA,
                          'dataFormat': [DEFAULT_EDAM_FORMAT],
                          'dataHandle': output['format'], 'dataDescription': output['name']
                          }
        listoutput.append(outputdict)
    return listoutput


# def extract_edam_from_galaxy(mapping_edam=None):
#    """
#    :param mapping_edam:
#    :return:
#    """
#    if not mapping_edam:
#        mapping_edam = {}
#    return mapping_edam


def build_edam_dict(yaml_file):
    """
    :param yaml_file:
    :return:
    """
    # map_edam = extract_edam_from_galaxy()
    with open(yaml_file, "r") as file_edam:
        map_edam = yaml.load(file_edam)
        for key, value in map_edam.iteritems():
            for term in value['formats']:
                term['uri'] = edam_to_uri(term['uri'], 'format')
            for term in value['data']:
                term['uri'] = edam_to_uri(term['uri'], 'data')
    return map_edam


def auth(login, host, ssl_verify):
    """
    :param login:
    :return:
    """
    key = None
    while key is None:
        password = getpass.getpass()
        url = host + '/api/rest-auth/login/'
        resp = requests.post(url, '{{"username": "{0}","password": "{1}"}}'.format(login, password),
                             headers={'Accept': 'application/json', 'Content-type': 'application/json'},
                             verify=ssl_verify)
        key = resp.json().get('key')
    return key


def push_to_elix(login, host, ssl_verify, tool_dir, resourcename, xsd=None):
    """
    :param login:
    :param tool_dir:
    :return:
    """
    logger.debug("authenticating...")
    token = auth(login, host, ssl_verify)
    logger.debug("authentication ok")
    ok_cnt = 0
    ko_cnt = 0
    logger.debug("attempting to retrieve registered services...")
    resp = requests.get(host + '/api/rest-auth/user/',
                        headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                 'Authorization': 'Token {0}'.format(token)})
    resources = resp.json().get('resources')
    logger.debug("attempting to delete all registered services in collection {0}...".format(resourcename))
    for resource in resources:
        try:
            logger.debug("checking resource {0}...".format(resource['id']))
            res_url = host + '/api/tool/{0}/version/{1}'.format(resource['id'], resource.get('version', 'none'))
            resp = requests.get(res_url, headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                                  'Authorization': 'Token {0}'.format(token)})
            if resp.status_code != 200:
                res_url = host + '/api/tool/{0}/version/none'.format(resource['id'])
                resp = requests.get(res_url, headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                                      'Authorization': 'Token {0}'.format(token)})
            res_full = resp.json()
            logger.debug('{0} in {1}: {2}'.format(resourcename, res_full.get(
                'collection', []), resourcename in res_full.get('collection', [])))
            if resourcename in res_full.get('collection', []):
                logger.debug("removing resource " + resource['id'])
                # FIXME added /version/none because not specifying it currently raises an error on dev.bio.tools :(
                resp = requests.delete(
                    res_url, headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                      'Authorization': 'Token {0}'.format(token)})
                if resp.status_code == 204:
                    logger.debug("{0} ok".format(resource['id']))
                else:
                    logger.error("{0} ko, error: {1} {2} (code: {3})".format(
                        resource['id'], resp.text, resp.status_code))
        except Exception:
            logger.error("Error removing resource {0}".format(resource['id']), exc_info=True)
    logger.debug("loading json")
    for jsonfile in glob.glob(os.path.join(tool_dir, "*.json")):
        json_string = open(jsonfile, 'r').read()
        url = host + "/api/tool"
        resp = requests.post(url, json_string,
                             headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                      'Authorization': 'Token {0}'.format(token)}, verify=ssl_verify)
        if resp.status_code == 201:
            logger.debug("{0} ok".format(os.path.basename(jsonfile)))
            ok_cnt += 1
        else:
            logger.error("{0} ko, error: {1}".format(os.path.basename(jsonfile), resp.text))
            ko_cnt += 1
#    if xsd:
#        xsdparse = etree.parse(xsd)
#    else:
#        xsdparse = etree.parse(os.path.join('$PREFIXDATA', 'biotools.xsd'))
#    schema = etree.XMLSchema(xsdparse)
#    parser = etree.XMLParser(schema = schema)
#    for xmlfile in glob.glob(os.path.join(tool_dir, "*.xml")):
#        try:
#            xmltree = etree.parse(xmlfile, parser)
#        except etree.XMLSyntaxError, err:
# print  "XML {0} is wrong formated, {1}".format(os.path.basename(xmlfile), err)
#            continue
#        url = host+"/api/tool"
#        resp = requests.post(url, etree.tostring(xmltree, pretty_print=True),
#                             headers={'Accept': 'application/json', 'Content-type': 'application/xml',
#                                      'Authorization': 'Token {0}'.format(token)}, verify=ssl_verify)
#        if resp.status_code == 201:
#            print "{0} ok".format(os.path.basename(xmlfile))
#            ok_cnt += 1
#        else:
#            print "{0} ko, error: {1}".format(os.path.basename(xmlfile), resp.text)
#            ko_cnt += 1
    logger.info("import finished, ok={0}, ko={1}".format(ok_cnt, ko_cnt))


def clean_list(jsonlist):
    """
    :param jsonlist:
    :return:
    """
    nullindexlist = []
    for elem in range(len(jsonlist)):
        if isinstance(jsonlist[elem], dict):
            clean_dict(jsonlist[elem])
        if isinstance(jsonlist[elem], list):
            clean_list(jsonlist[elem])
        if len(jsonlist[elem]) == 0:
            nullindexlist.append(elem)
    if nullindexlist:
        nullindexlist.sort(reverse=True)
        for i in nullindexlist:
            jsonlist.pop(i)
    return


def clean_dict(jsondict):
    """
    :param jsondict:
    :return:
    """
    for sonkey, sonvalue in jsondict.items():
        if sonvalue:
            if isinstance(sonvalue, dict):
                clean_dict(sonvalue)
            if isinstance(sonvalue, list):
                clean_list(sonvalue)

        if not sonvalue:
            del jsondict[sonkey]
    return


def write_json_files(tool_name, general_dict, tool_dir):
    """
    :param tool_name:
    :param general_dict:
    :return:
    """
    cleaned_dict = copy.deepcopy(general_dict)
    clean_dict(cleaned_dict)
    with open(os.path.join(tool_dir, tool_name + ".json"), 'w') as tool_file:
        json.dump(cleaned_dict, tool_file, indent=4)


def write_xml_files(tool_name, general_dict, tool_dir, xmltemplate=None):
    """
    :param tool_name:
    :param general_dict:
    :return:
    """
    if xmltemplate:
        template_path = xmltemplate
    else:
        template_path = get_data_path('xmltemplate.tmpl')

    with open(os.path.join(tool_dir, tool_name + ".xml"), 'w') as tool_file:
            template = Template(file=template_path, searchList=[general_dict])
            tool_file.write(str(template))


def build_biotools_files(tools_metadata, conf, mapping_edam):
    """
    :param tools_metadata:
    :return:
    """
    tool_dir = conf.tool_dir
    if os.path.exists(tool_dir):
        shutil.rmtree(tool_dir)
    os.mkdir(tool_dir)

    for tool_meta in tools_metadata:
        tool_name = build_tool_name(tool_meta[u'id'], conf.prefix_toolname, conf.suffix_toolname)
        general_dict = build_general_dict(tool_meta, conf)

        general_dict[u"function"] = build_function_dict(tool_meta, mapping_edam)
        # to obtain an uniq id in galaxy we need the toolshed repository, the owner, the xml toolid, the xml version,
        # if the tool provide from a toolshed, if not we need the xml toolid and the xml version only
        # The easiest : use id of the tool
        # general_dict[u"name"] = tool_meta[u'id']
        general_dict[u"name"] = tool_name
        general_dict[u"id"] = tool_name
        file_name = build_filename(tool_meta[u'id'], tool_meta[u'version'])
        write_json_files(file_name, general_dict, tool_dir)
        with open(tool_dir+'/'+file_name+'.yml', 'w') as outfile:
            yaml.safe_dump(tool_meta, outfile)
        # do not write XML files because they require source registry to be specified
        # if conf.xmltemplate:
        #    write_xml_files(file_name, general_dict, tool_dir,
        #                    xmltemplate=conf.xmltemplate)
        # else:
        #    write_xml_files(file_name, general_dict, tool_dir)


def generate_template():
    """
    :return:
    """
    template_config = get_data_path('regate.ini')
    with open(template_config, 'r') as configtemplate:
        with open('regate.ini', 'w') as fp:
            for line in configtemplate:
                fp.write(line)


def config_parser(configfile):
    """
    :param configfile:
    :return:
    """
    configuration = configparser.ConfigParser()
    configuration.read(configfile)
    return configuration


def run():
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    logging.getLogger("requests").setLevel(logging.ERROR)
    parser = argparse.ArgumentParser(description="Galaxy instance tool\
        parsing, for integration in biotools/bioregistry")
    parser.add_argument("--config_file", help="config.ini file for regate or remag")
    parser.add_argument("--templateconfig", action='store_true', help="generate a config_file template")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if not args.templateconfig:
        if not os.path.exists(args.config_file):
            raise IOError("{0} doesn't exist".format(args.config_file))
        config = Config(args.config_file, "regate")
        if not config.onlypush:
            gi = GalaxyInstance(config.galaxy_url_api, key=config.api_key)
            gi.verify = False
            try:
                TOOLS = gi.tools.get_tools()
            except ConnectionError, e:
                raise ConnectionError("Connection with the Galaxy server {0} failed, {1}".format(config.galaxy_url_api,
                                                                                                 e))

            tools_meta_data = []
            if config.yaml_file:
                edam_dict = build_edam_dict(config.yaml_file)
            else:
                edam_dict = build_edam_dict(get_data_path('yaml_mapping.yaml'))
            tools_list = config.tools_default.split(',')
            detect_toolid_duplicate(TOOLS)
            for tool in TOOLS:
                if not tool['id'] in tools_list:
                    try:
                        tool_metadata = gi.tools.show_tool(tool_id=tool['id'], io_details=True, link_details=True)
                        tools_meta_data.append(tool_metadata)
                    except ConnectionError, e:
                        logger.error(
                            "Error during connection with exposed API method for tool {0}".format(str(tool['id'])),
                            exc_info=True)
            build_biotools_files(tools_meta_data, config, edam_dict)

        if config.onlypush:
            tools_dir = config.tool_dir
            onlyfiles = [f for f in os.listdir(tools_dir) if os.path.isfile(os.path.join(tools_dir, f))]
            if len(onlyfiles) == 0:
                raise IOError("Error: Any file in {0}".format(tools_dir))

        if config.pushtoelixir:
            if config.xsdbiotools:
                push_to_elix(config.login, config.host, config.ssl_verify,
                             config.tool_dir, config.resourcename, xsd=config.xsdbiotools)
            else:
                push_to_elix(config.login, config.host, config.ssl_verify, config.tool_dir, config.resourcename)

    elif args.templateconfig:
        generate_template()
    else:
        parser.print_help()
