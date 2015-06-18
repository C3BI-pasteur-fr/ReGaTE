"""
Created on Oct. 23, 2014

@author: Olivia Doppelt-Azeroual, CIB-C3BI, Institut Pasteur, Paris
@author: Fabien Mareuil, CIB-C3BI, Institut Pasteur, Paris
@contact: olivia.doppelt@pasteur.fr
@project: toolinfowarehouse
@githuborganization: edamontology
"""

import sys
import os
import re
import pprint
import string
import argparse
import json
import yaml

from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy import GalaxyInstance


def build_tool_name(tool_id):
    """
    @tool_id: tool_id
    builds the tool_name regarding its toolshed id
   """
    #print tool_id
    id_list = string.split(tool_id, '/')
    return string.join(id_list[-2:], '_')


def get_source_registry(tool_id):
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


def build_metadata_one(tool_meta_data, url):
    """
      builds general_dict
      @param: tool_meta_data for one tool extracted from galaxy
    """

    if url == "https://galaxyapi.web.pasteur.fr":
        ressourceName = "Galaxy@pasteur"
        homepage = "https://galaxy.web.pasteur.fr"
    else:
        ressourceName = url
        homepage = url
#    gen_dict = {k: tool_meta_data[k] for k in (u'version', u'description')}

    gen_dict = {}
    gen_dict[u'version'] = tool_meta_data[u'version']
    gen_dict[u'description'] = format_description(tool_meta_data[u'description'])
    gen_dict[u'uses'] = [{"usesName": tool_meta_data[u'id'],
                          "usesHomepage": url,
                          "usesVersion": gen_dict[u'version']
        }]
    gen_dict[u'collection'] = ressourceName
    gen_dict[u'sourceRegistry'] = get_source_registry(tool_meta_data[u'id'])
    gen_dict[u'resourceType'] = [{"term": "Tool (analysis)", "uri": "http://www.cbs.dtu.dk/ontology/resource_type/7"}]
    gen_dict[u'maturity'] = [{u'uri': "",
                            u'term': 'production'
                            }]
    gen_dict[u'platform'] = [{u'uri': "",
                              u'term': 'Linux'
                              }]
    gen_dict[u'interface'] = [
        {u'interfaceType': {
            u'term': "WEB UI",
            u'uri': "http://www.cbs.dtu.dk/ontology/interface_type/3"
            }}
        ]
    gen_dict[u'contact'] = {
        u'contactEmail': 'galaxy@pasteur.fr',
        u'contactURL': '',
        u'contactName': 'Institut Pasteur galaxy team',
        u'contactRole': 'Computer Biologist'
        }
    # these fields need to be filled with MODULE ressource at Pasteur
    gen_dict[u'language'] = []
    gen_dict[u'topic'] = [{u'term': "", u'uri':"http://edamontology.org/topic_0003"}]
    gen_dict[u'tag'] = []
    gen_dict[u'license'] = []
    gen_dict[u'cost'] = []
    gen_dict[u'credits'] = []
    gen_dict[u'docs'] = []
    gen_dict[u'publications'] = []
    gen_dict[u'homepage'] = homepage
    gen_dict[u'accessibility'] = "private"

    return gen_dict


def build_case_inputs(case_dict, input):
    dict_cases = {}
    for inp in input[u'cases']:

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
                        if case[u'inputs'] != []:
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

    case_dict.update({i: j for i, j in dict_cases.items() if len(j) != 0})


def oldfind_edam_term(edam_name, edam_dict, cond):
    """
    edam_name: term to find in the edam_dict
    edam_dict: edam
    cond: term to not include is found because of edam_name
    """
    edam = ""
    for k, value in edam_dict.items():
        #print value[0], edam_name
        if (re.match(value[0], edam_name, re.IGNORECASE)) is not None and (re.match(r""+cond, k)) is None:
            return(k, value[1])
        else:
            edam = edam_name, "no uri"
    return edam

def edam_to_uri(edam):
    uri = re.split("_|:",edam)
    uri = "http://edamontology.org/{}_{:0>4d}".format(uri[1], int(uri[2]))
    return uri

def find_edam_format(format_name, edam_dict):
    if format_name in edam_dict:
        uri = edam_to_uri(edam_dict[format_name][0])
        return uri
    else:
        uri = "no uri"
        return uri
    
def find_edam_data(format_name, edam_dict):
    if format_name in edam_dict:
        list_uri = []
        temp_list = edam_dict[format_name][1:]
        if "EDAM_data:0006" in temp_list and len(temp_list) > 1:
            temp_list.remove("EDAM_data:0006")
        for edam_data in temp_list:
            if len(temp_list) == 1:
                uri = edam_to_uri(edam_data)
                list_uri.append(uri)
        return ", ".join(list_uri)
    else:
        uri = "no uri"
        return uri
    
def build_input_for_json(list_inputs, edam_dict):
    liste = []
    #inputs = {}
    #try:
    #    try:

    for input in list_inputs:
                inputDict = {}

                try:
                    formatList = input[u'extensions']
                except KeyError, e:
                    print e, "error 1"
                    formatList = ["AnyFormat"]
                    
                inputDict[u'dataType'] = []
                list_format = []
                for format in formatList:
                    uri = find_edam_format(format, edam_dict)
                    dict_format = {u'uri': uri, u'term': ''}
                    uri = find_edam_data(format, edam_dict)
                    inputDict[u'dataType'] = {u'uri': uri, u'term': ''}
                    list_format.append(dict_format)

                inputDict[u'dataFormat'] = list_format
                inputDict[u'dataHandle'] = ", ".join(input[u'extensions'])
                liste.append(inputDict)
                #pprint.pprint(inputDict)

    """
        except KeyError, e:
                print e, "error 2"
                formatList = input[u'extensions']
                for format in formatList:
                    uri = find_edam_data(format, edam_dict)
                    inputDict[u'dataType'].append({u'uri':uri, u'term': ''})
                    uri = find_edam_format(format, edam_dict)
                    inputDict[u'dataFormat'].append({u'uri': uri, u'term': ''})

                inputDict[u'dataHandle'] = ", ".join(input[u'extensions'])
                liste.append(inputDict)

    except KeyError, e:
        print e, "error 3"
        uri = find_edam_data(input[u'type'], edam_dict)
        inputDict[u'dataType'] = {u'uri': uri, u'term': ''}
        uri = find_edam_format(input[u'type'], edam_dict)
        inputDict[u'dataFormat'] = [{u'uri': uri, u'term': ''}]
        inputDict[u'dataHandle'] = ", ".join(input[u'extensions'])
        liste.append(inputDict)
    """
    return liste


def build_fonction_dict(tool_meta_data, edam_dict):
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
    inputs_case = {}

    for input in tool_meta_data[u'inputs']:
        if input[u'type'] == u'data':
            inputs_fix.append(input)
        # repeat not in conditional
        if input[u'type'] == u'repeat':
            for rep in input[u'inputs']:
                if rep[u'type'] == u'data':
                    inputs_fix.append(rep)
                elif rep[u'type'] == "conditional":
                    build_case_inputs(dict_cases, rep)
        if input[u'type'] == "conditional":
            build_case_inputs(dict_cases, input)

#__________________INPUT DICT _________________________
    if len(dict_cases) == 0:
        inputs["input_fix"] = build_input_for_json(inputs_fix, edam_dict)
    else:
        for key, case in dict_cases.iteritems():
            inputs[key] = build_input_for_json(case, edam_dict) + build_input_for_json(inputs_fix, edam_dict)

#_____________OUTPUT DICT_______________________________________

    for output in tool_meta_data[u'outputs']:
        outputDict = {}
        print output[u'format']
        uri = find_edam_data(output[u'format'], edam_dict)
        print uri
        outputDict[u'dataType'] = {u'uri': uri, u'term': ''}
        uri = find_edam_format(output[u'format'], edam_dict)
        outputDict[u'dataFormat'] = {u'uri': uri, u'term': ''}
        outputDict[u'dataHandle'] = output[u'format']
        outputs.append(outputDict)

    if inputs.get("input_fix") is None:
        for input_case_name, item in inputs.items():
            func_dict = {}
            func_dict[u'description'] = format_description(tool_meta_data[u'description'])
            func_dict[u'functionName'] = [{"uri":"http://edamontology.org/operation_0004"}]
            func_dict[u'output'] = outputs
            func_dict[u'input'] = item
            func_dict[u'functionHandle'] = input_case_name
            #func_dict[u'annot'] = input_case_name
            func_list.append(func_dict)
    else:
        func_dict[u'description'] = format_description(tool_meta_data[u'description'])
        func_dict[u'functionName'] = []
        func_dict[u'output'] = outputs
        func_dict[u'input'] = inputs[u"input_fix"]
        func_dict[u'functionHandle'] = 'MainFunction'
        func_list.append(func_dict)
    #pprint.pprint(func_list)
    return func_list

def extract_edam_from_galaxy(mapping_edam = {}):
    return mapping_edam

def build_edam_dict(edam_file):
    import yaml
    edam_dict = extract_edam_from_galaxy()
    with open(edam_file, "r") as file_edam:
        temp_edam_dict = yaml.load(file_edam)
    for key, value in temp_edam_dict.iteritems():
        if key in edam_dict:
            edam_dict[key] = edam_dict[key] + temp_edam_dict[key][1:]
        else:
            edam_dict[key] = temp_edam_dict[key]
    return edam_dict

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Galaxy instance tool\
        parsing, for integration in biotools/bioregistry")

    parser.add_argument("--galaxy_url", help="url to the analyze \
        galaxy instance")

    parser.add_argument("--api_key", help="galaxy user api key")

    parser.add_argument("--tool_dir", help="directory to store the tool\
        json (needs to be created before running the script")

    parser.add_argument("--collection_name", help="collection name \
        matchine the galaxy url")

    parser.add_argument("--edam_file", help="edam own file to create  \
        the edam_dict")

    parser.add_argument('--login', help="registry login")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    gi = GalaxyInstance(args.galaxy_url, key=args.api_key)

    tools = gi.tools.get_tools()

    tools_meta_data = []
    new_dict = {}
    json_ext = '.json'

    edam_dict = build_edam_dict(args.edam_file)

    for i in tools[0:20]:
        try:
            # improve this part, important to be able to get all tool from any toolshed
            if not i['id'].find("galaxy.web.pasteur.fr") or not i['id'].find("testtoolshed.g2.bx.psu.edu") or not i['id'].find("toolshed.g2.bx.psu.edu"):
                tool_metadata = gi.tools.show_tool(tool_id=i['id'], io_details=True, link_details=True)
                #pprint.pprint(tool_metadata)
                tools_meta_data.append(tool_metadata)
          #  else:
           #     print i['id']
        except ConnectionError:
            print "ConnectionError"
            pass

    for tool in tools_meta_data:
        tool_name = build_tool_name(tool[u'id'])
        try:

            function = build_fonction_dict(tool, edam_dict)
            with open(os.path.join(os.getcwd(), args.tool_dir, tool_name + json_ext), 'w') as tool_file:
                general_dict = build_metadata_one(tool, args.galaxy_url)
                general_dict[u"function"] = function
                general_dict[u"name"] = get_tool_name(tool[u'id'])
                json.dump(general_dict, tool_file, indent=4)

        except IOError:
            os.mkdir(os.path.join(os.getcwd(),args.tool_dir))
            with open(os.path.join(os.getcwd(), args.tool_dir, tool_name + json_ext), 'w') as tool_file:
                general_dict = build_metadata_one(tool, args.galaxy_url)
                general_dict[u"function"] = function
                general_dict[u"name"] = get_tool_name(tool[u'id'])
                json.dump(general_dict, tool_file, indent=4)
