#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Jun. 16, 2014

@author: Olivia Doppelt-Azeroual, CIB-C3BI, Institut Pasteur, Paris
@author: Fabien Mareuil, CIB-C3BI, Institut Pasteur, Paris
@contact: fabien.mareuil@pasteur.fr
@project: ReGaTE
@githuborganization: bioinfo-center-pasteur-fr
"""

import string
import os
import sys
import yaml
import rdflib
import xml.etree.ElementTree as ET
import argparse
import configparser

from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy.datatypes import DatatypesClient
from bioblend.galaxy.client import Client


class EdamDatatypesClient(DatatypesClient):
    """
    Override of the bioblend DatatypesClient class to add a get_edam_formats method
    """

    def get_edam_formats(self):
        """
        Displays a collection (dict) of edam formats.
        :rtype: dict
        :return: A dict of  individual edam_format.
                 For example::
             {
                "RData": "format_2333",
                "Roadmaps": "format_2561",
                "Sequences": "format_1929",
                "ab1": "format_2333",
                "acedb": "format_2330",
                "affybatch": "format_2331",
                "afg": "format_2561",
                "arff": "format_2330",
                "asn1": "format_2330",
                "asn1-binary": "format_2333"}
        """

        url = self.gi._make_url(self)
        url = '/'.join([url, "edam_formats"])

        return Client._get(self, url=url)


def is_true(value):
    """
    :param value:
    :return:
    """
    return value.lower() == "true"


def is_edamtype(dic_child):
    """
    :param dic_child:
    :return:
    """
    if 'edam' in dic_child:
        if dic_child['edam'] not in ['', "None", "Null"]:
            return True
        else:
            return False
    else:
        return False


def return_formatted_edam(edam):
    """
    :param edam:
    :return:
    """
    edam = string.split(edam, '_')
    edam = "EDAM_{}:{:0>4d}".format(edam[0], int(edam[1]))
    return edam


def tsv_to_dict(edam_mapping_file, mapping_dict):
    """
    Deprecated
    :param edam_mapping_file:
    :param mapping_dict:
    :return:
    """
    with open(edam_mapping_file, "r") as EG_MAPPING:
        for line in EG_MAPPING:
            splitted = string.split(line, '\t')
            if len(splitted) > 1 and splitted[0] not in ["GALAXY", "NAME", '"', "EXTENSION", '']:
                if splitted[1].strip() in ['']:
                    mapping_dict[splitted[0].strip()] = ["Not Mapped Yet"]
                else:
                    form_edam = return_formatted_edam(splitted[1].strip())
                    if splitted[0].strip() in mapping_dict:
                        if mapping_dict[splitted[0].strip()][0] != form_edam:
                            sys.stderr.write(
                                "MAPPING Incoherence between {0} and {1} for {2} extension, {3} have been chosen\n".format(
                                    mapping_dict[splitted[0].strip()][0], form_edam, splitted[0].strip(),
                                    mapping_dict[splitted[0].strip()][0]))

                    else:
                        mapping_dict[splitted[0].strip()] = [form_edam]
    return mapping_dict


def xml_to_dict(datatype_file_xml, mapping_dict):
    """
    Deprecated
    :param datatype_file_xml:
    :param mapping_dict:
    :return:
    """
    tree = ET.parse(datatype_file_xml)
    root = tree.getroot()
    for child in root[0]:
        if 'display_in_upload' in child.attrib:
            if is_edamtype(child.attrib):
                edam_format = return_formatted_edam(child.attrib['edam'])
                if not child.attrib['extension'] in mapping_dict and is_true(child.attrib['display_in_upload']):
                    mapping_dict[child.attrib['extension']] = [edam_format]
                else:
                    if mapping_dict[child.attrib['extension']][0] != edam_format:
                        sys.stderr.write(
                            "XML Incoherence between {0} and {1} for {2} extension, {3} have been chosen\n".format(
                                mapping_dict[child.attrib['extension']][0], edam_format, child.attrib['extension'],
                                mapping_dict[child.attrib['extension']][0]))
            else:
                if not child.attrib['extension'] in mapping_dict and is_true(child.attrib['display_in_upload']):
                    mapping_dict[child.attrib['extension']] = ["Not Mapped Yet"]
    return mapping_dict


def http_to_edamform(url):
    """
    :param url:
    :return:
    """
    base = string.split(os.path.basename(url), '_')
    return str("EDAM_{}:{:0>4d}").format(base[0], int(base[1]))


def edam_to_dict(edam_file):
    """
    :param edam_file:
    :return:
    """
    g = rdflib.Graph()
    g.parse(edam_file)
    query1 = """SELECT ?format ?is_format_of WHERE {
                      ?format rdfs:subClassOf ?format_sc .
                      ?format_sc owl:onProperty
                          <http://edamontology.org/is_format_of> .
                      ?format_sc owl:someValuesFrom ?is_format_of
                      }"""
    query2 = """SELECT ?format ?superformat WHERE {
                      ?format rdfs:subClassOf ?superformat .
                      ?superformat oboInOwl:inSubset <http://purl.obolibrary.org/obo/edam#formats>
                      }"""
    # Property = {"oboInOwl": "http://www.geneontology.org/formats/oboInOwl#"}
    format_with_formats = {}
    format_with_data = {}
    for row in g.query(query1):
        format_with_data[http_to_edamform(row[0])] = http_to_edamform(row[1])
    for row in g.query(query2):
        child_format = http_to_edamform(row[0])
        parent_format = http_to_edamform(row[1])
        if child_format in format_with_formats:
            format_with_formats[child_format].append(parent_format)
        else:
            format_with_formats[child_format] = [parent_format]
    return format_with_formats, format_with_data


def add_data(formats, relation_formats, relation_data, list_edam_data):
    """
    :param formats:
    :param relation_formats:
    :param relation_data:
    :param list_edam_data:
    :return:
    """
    if len(formats) != 0:
        for format_tool in formats:
            if format_tool in relation_data:
                list_edam_data.append(relation_data[format_tool])
                formats.remove(format_tool)
                return add_data(formats, relation_formats, relation_data, list_edam_data)
            elif format_tool in relation_formats:
                formats.remove(format_tool)
                formats = formats + relation_formats[format_tool]
                return add_data(formats, relation_formats, relation_data, list_edam_data)
            else:
                sys.stdout.write("NO FORMAT AND NO DATA FOR {0}\n".format(format_tool))
                formats.remove(format_tool)
                if format_tool in ("Not Mapped Yet", "NONE Known"):
                    return add_data(formats, relation_formats, relation_data, list_edam_data)
                else:
                    list_edam_data.append("EDAM_data:0006")
                    return add_data(formats, relation_formats, relation_data, list_edam_data)
    else:
        return list_edam_data


def add_datas(dict_map, relation_format_formats, relation_format_data):
    """
    :param dict_map:
    :param relation_format_formats:
    :param relation_format_data:
    :return:
    """
    import copy
    for key, value in dict_map.iteritems():
        formats = copy.copy(value)
        datas = add_data(formats, relation_format_formats, relation_format_data, list_edam_data=[])
        dict_map[key] = value + datas
    return dict_map


def dict_to_yaml(mapping_dict, yamlfile):
    """
    :param mapping_dict:
    :param yamlfile:
    :return:
    """
    stream = file(yamlfile, 'w')
    yaml.dump(mapping_dict, stream, default_flow_style=False)


def galaxy_to_edamdict(url, key, dict_map=None):
    """
    :param url:
    :param key:
    :param dict_map:
    :return:
    """
    if not dict_map:
        dict_map = {}
    gi = GalaxyInstance(url, key=key)
    datatypeclient = EdamDatatypesClient(gi)
    try:
        dict_map = datatypeclient.get_edam_formats()
    except ConnectionError, e:
        raise ConnectionError(
            '{0}, The Galaxy data can\'t be used, It\'s possible that Galaxy is too old, please update it\n'.format(e))
    dictmapping = {}
    for key, value in dict_map.iteritems():
        form_edam = return_formatted_edam(value)
        dictmapping[str(key)] = [form_edam]
    return dictmapping

def generate_template():
    """
    :return:
    """
    TEMPLATE_CONFIG = os.path.join('$PREFIXDATA', 'regate.ini')
    with open( TEMPLATE_CONFIG, 'r') as configtemplate:
        with open('regate.ini', 'w') as fp:
            for line in configtemplate:
                fp.write(line)

def config_parser(configfile):
    """
    :param configfile:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(configfile)
    return config


if __name__ == "__main__":
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
        config = config_parser(args.config_file)
        if 'galaxy_url_api' and 'api_key' in config['galaxy_server'] and config.get('galaxy_server', 'galaxy_url_api') and config.get('galaxy_server', 'api_key'):
            dict_mapping = galaxy_to_edamdict(config.get('galaxy_server', 'galaxy_url_api'), config.get('galaxy_server', 'api_key'))
        else:
            raise KeyError("galaxy_url_api or api_key option doesn't exist in {0}".format(args.config_file))


        if 'edam_file' in config['remag_specific_section'] and config.get('remag_specific_section', 'edam_file'):
            relation_format_formats, relation_format_data = edam_to_dict(config.get('remag_specific_section', 'edam_file'))
        else:
            raise KeyError("edam_file option doesn't exist in {0}".format(args.config_file))

        if 'output_yaml' in config['remag_specific_section'] and config.get('remag_specific_section', 'output_yaml'):
            yaml_file = config.get('remag_specific_section', 'output_yaml')
            dict_mapping = add_datas(dict_mapping, relation_format_formats, relation_format_data)

            dict_to_yaml(dict_mapping, yaml_file)
        else:
            raise KeyError("output_yaml option doesn't exist in {0}".format(args.config_file))
    elif args.templateconfig:
        generate_template()
    else:
        parser.print_help()
