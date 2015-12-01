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
import remag

from Cheetah.Template import Template
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy import GalaxyInstance

from logging.handlers import RotatingFileHandler

def build_tool_name(tool_id):
    """
    @tool_id: tool_id
    builds the tool_name regarding its toolshed id
   """
    # print tool_id
    id_list = string.split(tool_id, '/')
    return string.join(id_list[-2:], '_')


def get_source_registry(tool_id):
    """
    :param tool_id:
    :return:
    """
    try:
        source = string.split(tool_id, '/')
        return "https://" + '/'.join(source[0:len(source) - 2])
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
    ressourcename = conf.get('galaxy_server', 'ressourcename')
    #    gen_dict = {k: tool_meta_data[k] for k in (u'version', u'description')}

    gen_dict = {}
    gen_dict[u'version'] = tool_meta_data[u'version']
    gen_dict[u'description'] = format_description(tool_meta_data[u'description'])
    gen_dict[u'uses'] = [{"usesName": tool_meta_data[u'id'],
                          "usesHomepage":  "{0}?tool_id={1}".format(
                                                        os.path.join(conf.get('galaxy_server', 'galaxy_url'),"root"),
                                                        tool_meta_data[u'id']
                                                        ),
                          "usesVersion": gen_dict[u'version']
                          }]
    gen_dict[u'collection'] = [ressourcename]
    gen_dict[u'sourceRegistry'] = get_source_registry(tool_meta_data[u'id'])
    gen_dict[u'resourceType'] = ["Tool"]
    gen_dict[u'maturity'] = 'Established'

    gen_dict[u'platform'] = [{u'term': 'Linux'}]
    gen_dict[u'interface'] = [
        {u'interfaceType': "WEB UI",
        u'interfaceDocs': '',
        u'interfaceSpecURL':'',
        u'interfaceSpecFormat':''}]
    # these fields need to be filled with MODULE ressource at Pasteur
    # gen_dict[u'language'] = []
    gen_dict[u'topic'] = [{u'uri': "http://edamontology.org/topic_0003",
                           u'term' : "EDAM label placeholder"}]
    gen_dict[u'credits'] = []
    gen_dict[u'publications'] = {u'publicationsPrimaryID': "None", u'publicationsOtherID' : []}
    gen_dict[u'homepage'] = conf.get('galaxy_server', 'galaxy_url')
    gen_dict[u'accessibility'] = "private"
    gen_dict[u'mirror'] = []
    gen_dict[u'canonicalID'] = ''
    gen_dict[u'tag'] = []
    gen_dict[u'elixirInfo'] = {u'elixirStatus' :'',
                            u'elixirNode':''}
    gen_dict[u'platform'] = []
    gen_dict[u'language'] = []
    gen_dict[u'license'] = ''
    gen_dict[u'cost'] = ''
    gen_dict[u'docs'] = {u'docsHome': '',
                    u'docsTermsOfUse': '',
                    u'docsDownload': '',
                    u'docsCitationInstructions': ''}
    gen_dict[u'credits'] = {u'creditsDeveloper': [],
                            u'creditsContributor': [],
                            u'creditsInstitution': [],
                            u'creditsInfrastructure': [],
                            u'creditsFunding': []}
    gen_dict[u'contact'] = [{u'contactEmail': conf.get('galaxy_server', 'contactEmail'),
                            u'contactURL': '',
                            u'contactName': conf.get('galaxy_server', 'contactName'),
                            u'contactTel': '',
                            u'contactRole': []}]
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
        logger.warning("EDAM MAPPING: TERM ----{}---- is missing from EDAM current version".format(format_name))
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
        inputdict = {}
        try:
            formatlist = input_tool[u'extensions']
        except KeyError, e:
            print e, "error 1"
            formatlist = ["AnyFormat"]

        inputdict[u'dataType'] = []
        list_format = []
        for format_tool in formatlist:
            uri = find_edam_format(format_tool, mapping_edam)
            dict_format = {u'uri': uri, u'term': 'EDAM label placeholder'}
            list_format.append(dict_format)
        data_uri = find_edam_data(formatlist[0], mapping_edam)
        if data_uri:
            data_uri = "http://edamontology.org/data_0006"
            logger.warning("EDAM MAPPING: TERM ----{}---- is missing from EDAM current version".format(formatlist[0]))
        inputdict[u'dataType'] = {u'uri': data_uri, u'term': 'EDAM label placeholder'}
        inputdict[u'dataFormat'] = list_format
        inputdict[u'dataHandle'] = ", ".join(input_tool[u'extensions'])
        inputdict[u'dataDescription'] = ''
        liste.append(inputdict)
    return liste


def build_fonction_dict(tool_meta_data, mapping_edam):
    """
    builds function dict
    2 steps for inputs, get only the data format and
    dict comprehension to keep only important info
    1 steps for outputs, only dict comprehension
    """
    func_dict = {}
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
        outputdict = {}
        data_uri = find_edam_data(output[u'format'], mapping_edam)
        if data_uri == []:
            data_uri = "http://edamontology.org/data_0006"
            # put a logger here to get the missing format
            logger.warning("EDAM MAPPING: TERM ----{}---- is missing from EDAM current version".format(output[u'format']))
        # print tool_meta_data['name'], term
        uri = find_edam_format(output[u'format'], mapping_edam)
        outputdict[u'dataType'] = {u'uri': data_uri, u'term': 'EDAM label placeholder'}
        outputdict[u'dataFormat'] = [{u'uri': uri, u'term': 'EDAM label placeholder'}]
        outputdict[u'dataHandle'] = ''
        outputdict[u'dataDescription'] = ''
        outputs.append(outputdict)

    if inputs.get("input_fix") is None:
        for input_case_name, item in inputs.items():
            func_dict = {}
            func_dict[u'functionDescription'] = format_description(tool_meta_data[u'description'])
            func_dict[u'functionName'] = [{u'uri': "http://edamontology.org/operation_0004", u'term' : 'EDAM label placeholder'}]
            func_dict[u'output'] = outputs
            func_dict[u'input'] = item
            func_dict[u'functionHandle'] = input_case_name
            # func_dict[u'annot'] = input_case_name
            func_list.append(func_dict)
    else:
        func_dict[u'functionDescription'] = format_description(tool_meta_data[u'description'])
        func_dict[u'functionName'] = []
        func_dict[u'output'] = outputs
        func_dict[u'input'] = inputs[u"input_fix"]
        func_dict[u'functionHandle'] = 'MainFunction'
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


def auth(login):
    """
    :param login:
    :return:
    """
    password = getpass.getpass()
    resp = requests.post('https://elixir-registry.cbs.dtu.dk/api/auth/login',
                         '{"username": "%s","password": "%s"}' % (login, password),
                         headers={'Accept': 'application/json', 'Content-type': 'application/json'}).text
    return json.loads(resp)['token']


def push_to_elix(login, tool_dir):
    """
    :param login:
    :param tool_dir:
    :return:
    """
    print "authenticating..."
    token = auth(login)
    print "authentication ok"
    ok_cnt = 0
    ko_cnt = 0
    print "attempting to delete all registered services..."
    resp = requests.delete('https://elixir-registry.cbs.dtu.dk/api/tool/%s' % login,
                           headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                    'Authorization': 'Token %s' % token})
    print resp
    print resp.headers
    print resp.status_code
    pprint.pprint(resp)

    print "loading json"
    print os.getcwd()
    path = os.path.join(os.getcwd(), tool_dir)
    for jsonfile in os.listdir(tool_dir):
        with open(os.path.join(path, jsonfile), 'r') as json_file:
            json_data = json.load(json_file)
            resp = requests.post('https://elixir-registry.cbs.dtu.dk/api/tool', json.dumps(json_data),
                                 headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                          'Authorization': 'Token %s' % token})
            if resp.status_code == 201:
                print "%s ok" % jsonfile
                ok_cnt += 1
            else:
                print "%s ko, error: %s" % (jsonfile, resp.text)
                ko_cnt += 1
    print "import finished, ok=%s, ko=%s" % (ok_cnt, ko_cnt)

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
        TEMPLATE_PATH = xmltemplate
    else:
        TEMPLATE_PATH = os.path.join('$PREFIXDATA','xmltemplate.tmpl')

    if not os.path.exists(tool_dir):
        os.mkdir(tool_dir)
    with open(os.path.join(tool_dir, tool_name + ".xml"), 'w') as tool_file:
            template = Template(file=TEMPLATE_PATH, searchList=[general_dict])
            tool_file.write(str(template))

def build_outputs(tools_meta_data, conf, mapping_edam):
    """
    :param tools_meta_data:
    :return:
    """
    for tool in tools_meta_data:
        tool_name = build_tool_name(tool[u'id'])
        function = build_fonction_dict(tool, mapping_edam)
        general_dict = build_metadata_one(tool, conf)
        general_dict[u"function"] = function
        #general_dict[u"name"] = get_tool_name(tool[u'id'])
        general_dict[u"name"] = tool[u'name']
        write_json_files(tool_name, general_dict, conf.get('regate_specific_section', 'tool_dir'))
        if 'xmltemplate' in conf['regate_specific_section']:
            write_xml_files(tool_name, general_dict, conf.get('regate_specific_section', 'tool_dir'),
                            xmltemplate=conf.get('regate_specific_section', 'xmltemplate'))
        else:
            write_xml_files(tool_name, general_dict, conf.get('regate_specific_section', 'tool_dir'))

def config_parser(configfile):
    """
    :param configfile:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(configfile)
    return config

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
        config = remag.config_parser(args.config_file)

        if not 'onlypush' in config['regate_specific_section'] or not config.getboolean('regate_specific_section', 'onlypush'):
            gi = GalaxyInstance(config.get('galaxy_server', 'galaxy_url_api'), key=config.get('galaxy_server', 'api_key'))
            gi.verify = False
            try:
                TOOLS = gi.tools.get_tools()
            except ConnectionError, e:
                    raise ConnectionError("Connection with the Galaxy server {0} failed, {1}".format(config.get('galaxy_server', 'galaxy_url_api'), e))

            tools_meta_data = []
            edam_dict = build_edam_dict(config.get('regate_specific_section', 'yaml_file'))
            tools_list = config.get('galaxy_server','tools_default').split(',')
            for tool in TOOLS:
                if not tool['id'] in tools_list:
                    tool_metadata = gi.tools.show_tool(tool_id=tool['id'], io_details=True, link_details=True)
                    tools_meta_data.append(tool_metadata)

            build_outputs(tools_meta_data, config, edam_dict)

        if 'onlypush' in config['regate_specific_section'] and config.getboolean('regate_specific_section', 'onlypush'):
            if not 'pushtoelixir' in config['regate_specific_section'] or not config.getboolean('regate_specific_section', 'pushtoelixir'):
                raise KeyError("with onlypush argument pushtoelixir argument is required")
            else:
                tools_dir = config.get('regate_specific_section', 'tool_dir')
                onlyfiles = [f for f in os.listdir(tools_dir) if os.path.isfile(os.path.join(tools_dir, f))]
                if len(onlyfiles) == 0:
                    raise IOError("Error: Any file in {0}".format(tools_dir))

        if 'pushtoelixir' in config['regate_specific_section'] and config.getboolean('regate_specific_section', 'pushtoelixir'):
            if not 'login' in config['regate_specific_section'] or not config.get('regate_specific_section', 'login'):
                raise KeyError("with pushtoelixir argument login elixir registry argument is required you can relaunch regate with just the onlypush option to True after login correction")
            else:
                push_to_elix(config.get('regate_specific_section','login'), config.get('regate_specific_section', 'tool_dir'))

    elif args.templateconfig:
        remag.generate_template()
    else:
        parser.print_help()
