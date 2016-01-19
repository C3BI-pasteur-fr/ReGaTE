#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct. 23, 2014

@author: Olivia Doppelt-Azeroual, CIB-C3BI, Institut Pasteur, Paris
@author: Fabien Mareuil, CIB-C3BI, Institut Pasteur, Paris
@contact: olivia.doppelt@pasteur.fr
@project: ReGaTE
@githuborganization: C3BI-pasteur-fr
"""

import sys
import os
import glob
import re
import pprint
import string
import argparse
import json
import yaml
import requests
import getpass
import copy
import logging
import configparser

from lxml import etree

from Cheetah.Template import Template
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy import GalaxyInstance

from logging.handlers import RotatingFileHandler


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
            self.ressourcename = self.assign("galaxy_server", "ressourcename", ismandatory=True)
            self.onlypush = self.assign("regate_specific_section", "onlypush", ismandatory=False, boolean=True)
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
                self.private = self.assign("regate_specific_section", "private", ismandatory=True,
                                                 message="private option is mandatory if pushtoelixir is True",
                                                 boolean=True)
            else:
                self.login = self.assign("regate_specific_section", "login", ismandatory=False)
                self.host = self.assign("regate_specific_section", "bioregistry_host", ismandatory=False)
                self.ssl_verify = self.assign("regate_specific_section", "ssl_verify", ismandatory=False, boolean=True)
            self.private = self.assign("regate_specific_section", "private", ismandatory=True, boolean=True)
            self.tool_dir = self.assign("regate_specific_section", "tool_dir", ismandatory=True)
            self.yaml_file = self.assign("regate_specific_section", "yaml_file", ismandatory=False)
            self.xmltemplate = self.assign("regate_specific_section", "xmltemplate", ismandatory=False)
            self.xsdbiotools = self.assign("regate_specific_section", "xsdbiotools", ismandatory=False)
        if script == "remag":
            self.edam_file = self.assign("remag_specific_section", "edam_file", ismandatory=True)
            self.output_yaml = self.assign("remag_specific_section", "output_yaml", ismandatory=True)

    def assign(self, section, key, ismandatory=True, message=None, boolean=False):
        """
            return value if key exist in config.ini file or an error or None if not, depending on whether the option
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


def build_tool_name(tool_id):
    """
    @tool_id: tool_id
    builds the tool_name regarding its toolshed id
   """
    tbl = string.maketrans('.:/','___')
    #warning unicode is not string
    return str(tool_id).translate(tbl)


def get_source_registry(tool_id):
    """
    :param tool_id:
    :return:
    """
    try:
        return "/".join(tool_id.replace('repos','view',1).split('/')[0:-2])
    except ValueError:
        print "ValueError:", tool_id
        return ""


def get_tool_name(tool_id):
    try:
        source = string.split(tool_id, '/')[-2]
        return source
    except ValueError:
        print "ValueError:", tool_id
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
        print description


def build_metadata_one(tool_meta_data, conf):
    """
      builds general_dict
      @param: tool_meta_data for one tool extracted from galaxy
    """
    #    gen_dict = {k: tool_meta_data[k] for k in (u'version', u'description')}

    gen_dict = {
        u'version': tool_meta_data[u'version'],
        u'description': format_description(tool_meta_data[u'description']),
        u'uses': [{
            "usesName": tool_meta_data[u'id'],
            "usesHomepage": "{0}?tool_id={1}".format(os.path.join(conf.galaxy_url, "root"),
                                                     tool_meta_data[u'id']),
            "usesVersion": tool_meta_data[u'version']
        }],
        u'collection': [conf.ressourcename],
        u'sourceRegistry': get_source_registry(tool_meta_data[u'id']),
        u'resourceType': ["Tool"],
        u'maturity': 'Stable',
        u'platform': [{u'term': 'Linux'}],
        u'interface': [{
            u'interfaceType': "Web UI",
            u'interfaceDocs': '',
            u'interfaceSpecURL': '',
            u'interfaceSpecFormat': ''
        }],
        # these fields need to be filled with MODULE ressource at Pasteur
        #  gen_dict[u'language'] = []
        u'topic': [{
            u'uri': "http://edamontology.org/topic_0003",
            u'term': "EDAM label placeholder"
        }],
        u'publications': {u'publicationsPrimaryID': "None", u'publicationsOtherID': []},
        u'homepage': conf.galaxy_url,
        u'accessibility': "Private" if conf.private else "Public",
        u'mirror': [],
        u'canonicalID': '',
        u'tag': [],
        u'elixirInfo': {
            u'elixirStatus': '',
            u'elixirNode': ''
        },
        u'language': [],
        u'license': '',
        u'cost': '',
        u'docs': {
            u'docsHome': '',
            u'docsTermsOfUse': '',
            u'docsDownload': '',
            u'docsCitationInstructions': ''
        },
        u'credits': {
            u'creditsDeveloper': [],
            u'creditsContributor': [],
            u'creditsInstitution': [],
            u'creditsInfrastructure': [],
            u'creditsFunding': []
        },
        u'contact': [{
            u'contactEmail': conf.contactEmail,
            u'contactURL': '',
            u'contactName': conf.contactName,
            u'contactTel': '',
            u'contactRole': []
        }]
    }
    return gen_dict


def build_case_inputs(case_dict, input_tool):
    """
    :param case_dict:
    :param input_tool:
    :return:
    """
    dict_cases = {}
    for inp in input_tool[u'cases']:

        for elem in inp[u'inputs']:
            if elem[u'type'] == u'data':
                if dict_cases.get(inp[u'value']) is None:
                    dict_cases[inp[u'value']] = [elem]
                else:
                    dict_cases[inp[u'value']].append(elem)

                    # repeat in conditional

            if elem[u'type'] == u'repeat':
                try:
                    cases = elem[u'inputs'][0][u'cases']

                    for case in cases:
                        if case[u'inputs']:
                            for case_input in case[u'inputs']:
                                if case_input[u'type'] == u'data':
                                    if dict_cases.get(inp[u'value']) is None:
                                        dict_cases[inp[u'value']] = [case_input]
                                    else:
                                        dict_cases[inp[u'value']].append(case_input)

                except KeyError:
                    #                    print "KeyError key == REPEAT"
                    for el in elem[u'inputs']:
                        if el[u'type'] == u'data':
                            if dict_cases.get(inp[u'value']) is None:
                                dict_cases[inp[u'value']] = [el]
                            else:
                                dict_cases[inp[u'value']].append(el)

    case_dict.update({key: value for key, value in dict_cases.items() if len(value) != 0})


def edam_to_uri(edam):
    """
    :param edam:
    :return:
    """
    uri = re.split("_|:", edam)
    uri = "http://edamontology.org/{}_{:0>4d}".format(uri[1], int(uri[2]))
    return uri


def find_edam_format(format_name, mapping_edam):
    """
    :param format_name:
    :param mapping_edam:
    :return:
    """
    if format_name in mapping_edam:
        uri = edam_to_uri(mapping_edam[format_name][0])
        return uri
    else:
        uri = "http://edamontology.org/format_1915"
        logger.warning("EDAM MAPPING: TERM ----{0}---- is missing from EDAM current version".format(format_name))
        return uri


def find_edam_data(format_name, mapping_edam):
    """
    :param format_name:
    :param mapping_edam:
    :return:
    """
    if format_name in mapping_edam:
        list_uri = []
        temp_list = mapping_edam[format_name][1:]
        if "EDAM_data:0006" in temp_list and len(temp_list) > 1:
            temp_list.remove("EDAM_data:0006")
        if len(temp_list) == 1:
            uri = edam_to_uri(temp_list[0])
            list_uri.append(uri)
        else:
            uri = edam_to_uri(temp_list[0])
            list_uri.append(uri)

        return ", ".join(list_uri)
    else:
        return []


def build_input_for_json(list_inputs, mapping_edam):
    """
    :param list_inputs:
    :param mapping_edam:
    :return:
    """
    liste = []
    for input_tool in list_inputs:
        try:
            formatlist = input_tool[u'extensions']
        except KeyError, err:
            print err, "error 1"
            formatlist = ["AnyFormat"]

        list_format = []
        for format_tool in formatlist:
            uri = find_edam_format(format_tool, mapping_edam)
            dict_format = {u'uri': uri, u'term': 'EDAM label placeholder'}
            list_format.append(dict_format)
        data_uri = find_edam_data(formatlist[0], mapping_edam)
        if data_uri:
            data_uri = "http://edamontology.org/data_0006"
            logger.warning("EDAM MAPPING: TERM ----{0}---- is missing from EDAM current version".format(formatlist[0]))
        inputdict = {
            u'dataType': {u'uri': data_uri, u'term': 'EDAM label placeholder'},
            u'dataFormat': list_format,
            u'dataHandle': ", ".join(input_tool[u'extensions']),
            u'dataDescription': ''
        }
        liste.append(inputdict)
    return liste


def build_fonction_dict(tool_meta_data, mapping_edam):
    """
    builds function dict
    2 steps for inputs, get only the data format and
    dict comprehension to keep only important info
    1 steps for outputs, only dict comprehension
    """
    func_list = []
    inputs = {}
    outputs = []
    inputs_fix = []
    dict_cases = {}
    # inputs_case = {}

    for input_tool in tool_meta_data[u'inputs']:
        if input_tool[u'type'] == u'data':
            inputs_fix.append(input_tool)
        # repeat not in conditional
        if input_tool[u'type'] == u'repeat':
            for rep in input_tool[u'inputs']:
                if rep[u'type'] == u'data':
                    inputs_fix.append(rep)
                elif rep[u'type'] == "conditional":
                    build_case_inputs(dict_cases, rep)
        if input_tool[u'type'] == "conditional":
            build_case_inputs(dict_cases, input_tool)

            # __________________INPUT DICT _________________________
    if len(dict_cases) == 0:
        inputs["input_fix"] = build_input_for_json(inputs_fix, mapping_edam)
    else:
        for key, case in dict_cases.iteritems():
            inputs[key] = build_input_for_json(case, mapping_edam) + build_input_for_json(inputs_fix, mapping_edam)

            # _____________OUTPUT DICT_______________________________________

    for output in tool_meta_data[u'outputs']:
        data_uri = find_edam_data(output[u'format'], mapping_edam)
        if data_uri:
            data_uri = "http://edamontology.org/data_0006"
            # put a logger here to get the missing format
            logger.warning("EDAM MAPPING: TERM ----{0}---- is missing from EDAM current version".format(
                output[u'format']))
        # print tool_meta_data['name'], term
        uri = find_edam_format(output[u'format'], mapping_edam)
        outputdict = {
            u'dataType': {u'uri': data_uri, u'term': 'EDAM label placeholder'},
            u'dataFormat': [{u'uri': uri, u'term': 'EDAM label placeholder'}],
            u'dataHandle': '',
            u'dataDescription': ''
        }
        outputs.append(outputdict)

    if inputs.get("input_fix") is None:
        for input_case_name, item in inputs.items():
            func_dict = {
                u'functionDescription': format_description(tool_meta_data[u'description']),
                u'functionName': [{
                    u'uri': "http://edamontology.org/operation_0004",
                    u'term': 'EDAM label placeholder'
                }],
                u'output': outputs,
                u'input': item,
                u'functionHandle': input_case_name
                # func_dict[u'annot'] = input_case_name
            }
            func_list.append(func_dict)
    else:
        func_dict = {
            u'functionDescription': format_description(tool_meta_data[u'description']),
            u'functionName': [{
                u'uri': "http://edamontology.org/operation_0004",
                u'term': 'EDAM label placeholder'
            }],
            u'output': outputs,
            u'input': inputs[u"input_fix"],
            u'functionHandle': 'MainFunction'
        }
        func_list.append(func_dict)
    return func_list


def extract_edam_from_galaxy(mapping_edam=None):
    """
    :param mapping_edam:
    :return:
    """
    if not mapping_edam:
        mapping_edam = {}
    return mapping_edam


def build_edam_dict(yaml_file):
    """
    :param yaml_file:
    :return:
    """
    map_edam = extract_edam_from_galaxy()
    with open(yaml_file, "r") as file_edam:
        temp_map_edam = yaml.load(file_edam)
    for key, value in temp_map_edam.iteritems():
        if key in map_edam:
            map_edam[key] = map_edam[key] + temp_map_edam[key][1:]
        else:
            map_edam[key] = temp_map_edam[key]
    return map_edam


def auth(login, host, ssl_verify):
    """
    :param login:
    :return:
    """
    password = getpass.getpass()
    resp = requests.post(os.path.join(host, '/api/auth/login'),
                         '{"username": "{0},"password": {1}}'.format(login, password),
                         headers={'Accept': 'application/json', 'Content-type': 'application/json'},
                         verify=ssl_verify).text
    return json.loads(resp)['token']


def push_to_elix(login, host, ssl_verify, tool_dir, xsd=None):
    """
    :param login:
    :param tool_dir:
    :return:
    """
    print "authenticating..."
    token = auth(login, host, ssl_verify)
    print "authentication ok"
    ok_cnt = 0
    ko_cnt = 0
    print "attempting to delete all registered services..."
    resp = requests.delete(os.path.join(host, '/api/tool/{0}'.format(login)),
                           headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                    'Authorization': 'Token {0}'.format(token)})
    print resp
    print resp.headers
    print resp.status_code
    pprint.pprint(resp)
    print "loading json"
    if xsd:
        xsdparse = etree.parse(xsd)
    else:
        xsdparse = etree.parse(os.path.join('$PREFIXDATA', 'biotools.xsd'))
    schema = etree.XMLSchema(xsdparse)
    parser = etree.XMLParser(schema = schema)
    for xmlfile in glob.glob(os.path.join(tool_dir, "*.xml")):
        try:
            xmltree = etree.parse(xmlfile, parser)
        except etree.XMLSyntaxError, err:
            print  "XML {0} is wrong formated, {1}".format(os.path.basename(xmlfile), err)
        resp = requests.post(os.path.join(host, '/api/tool'), etree.tostring(xmltree, pretty_print=True),
                             headers={'Accept': 'application/json', 'Content-type': 'application/xml',
                                      'Authorization': 'Token {0}'.format(token)}, verify=ssl_verify)
        if resp.status_code == 201:
            print "{0} ok".format(os.path.basename(xmlfile))
            ok_cnt += 1
        else:
            print "{0} ko, error: {1}".format(os.path.basename(xmlfile), resp.text)
            ko_cnt += 1
    print "import finished, ok={0}, ko={1}".format(ok_cnt, ko_cnt)


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
    if not os.path.exists(tool_dir):
        os.mkdir(tool_dir)
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
        template_path = os.path.join('$PREFIXDATA', 'xmltemplate.tmpl')

    if not os.path.exists(tool_dir):
        os.mkdir(tool_dir)
    with open(os.path.join(tool_dir, tool_name + ".xml"), 'w') as tool_file:
            template = Template(file=template_path, searchList=[general_dict])
            tool_file.write(str(template))


def build_outputs(tools_metadata, conf, mapping_edam):
    """
    :param tools_metadata:
    :return:
    """
    for tool_meta in tools_metadata:
        tool_name = build_tool_name(tool_meta[u'id'])
        function = build_fonction_dict(tool_meta, mapping_edam)
        general_dict = build_metadata_one(tool_meta, conf)
        general_dict[u"function"] = function
        # to obtain an uniq id in galaxy we need the toolshed repository, the owner, the xml toolid, the xml version,
        # if the tool provide from a toolshed, if not we need the xml toolid and the xml version only
        # The easiest : use id of the tool
        # general_dict[u"name"] = tool_meta[u'id']
        general_dict[u"name"] = tool_name
        write_json_files(tool_name, general_dict, conf.tool_dir)
        if conf.xmltemplate:
            write_xml_files(tool_name, general_dict, conf.tool_dir,
                            xmltemplate=conf.xmltemplate)
        else:
            write_xml_files(tool_name, general_dict, conf.tool_dir)


def generate_template():
    """
    :return:
    """
    template_config = os.path.join('$PREFIXDATA', 'regate.ini')
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


if __name__ == "__main__":

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

    # first logger
    file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # second logger
    file_handler_edam = RotatingFileHandler('edam_mapping.log', 'a', 1000000, 1)

    file_handler_edam.setLevel(logging.WARNING)
    file_handler_edam.setFormatter(formatter)
    logger.addHandler(file_handler_edam)

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
                edam_dict = build_edam_dict(os.path.join('$PREFIXDATA', 'yaml_mapping.yaml'))

            tools_list = config.tools_default.split(',')
            for tool in TOOLS:
                if not tool['id'] in tools_list:
                    tool_metadata = gi.tools.show_tool(tool_id=tool['id'], io_details=True, link_details=True)
                    tools_meta_data.append(tool_metadata)

            build_outputs(tools_meta_data, config, edam_dict)

        if config.onlypush:
            tools_dir = config.tool_dir
            onlyfiles = [f for f in os.listdir(tools_dir) if os.path.isfile(os.path.join(tools_dir, f))]
            if len(onlyfiles) == 0:
                raise IOError("Error: Any file in {0}".format(tools_dir))

        if config.pushtoelixir:
            if config.xsdbiotools:
                push_to_elix(config.login, config.host, config.ssl_verify, config.tool_dir, xsd=config.xsdbiotools)
            else:
                push_to_elix(config.login, config.host, config.ssl_verify, config.tool_dir)

    elif args.templateconfig:
        generate_template()
    else:
        parser.print_help()
