#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Jun. 16, 2014

@author: Olivia Doppelt-Azeroual, CIB-C3BI, Institut Pasteur, Paris
@author: Fabien Mareuil, CIB-C3BI, Institut Pasteur, Paris
@author: Hervé Ménager, CIB-C3BI, Institut Pasteur, Paris
@contact: fabien.mareuil@pasteur.fr
@project: ReGaTE
@githuborganization: bioinfo-center-pasteur-fr
"""

import string
import os
import sys
import yaml
import rdflib
import argparse
import regate

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
    query3 = """SELECT ?format ?label WHERE {
                      ?format rdfs:label ?label.
                      ?format oboInOwl:inSubset ?subset.
                      FILTER (?subset = <http://purl.obolibrary.org/obo/edam#formats> ||
                              ?subset = <http://purl.obolibrary.org/obo/edam#data>)}"""
    # Property = {"oboInOwl": "http://www.geneontology.org/formats/oboInOwl#"}
    format_with_formats = {}
    format_with_data = {}
    term_labels = {}
    for row in g.query(query1):
        format_with_data[http_to_edamform(row[0])] = http_to_edamform(row[1])
    for row in g.query(query2):
        child_format = http_to_edamform(row[0])
        parent_format = http_to_edamform(row[1])
        if child_format in format_with_formats:
            format_with_formats[child_format].append(parent_format)
        else:
            format_with_formats[child_format] = [parent_format]
    for row in g.query(query3):
        term_labels[http_to_edamform(row[0].toPython())]=str(row[1].toPython())
    return format_with_formats, format_with_data, term_labels


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


def add_datas(dict_map, rel_format_formats, rel_format_data, term_labels):
    """
    :param dict_map:
    :param rel_format_formats:
    :param rel_format_data:
    :return:
    """
    import copy
    for key, value in dict_map.iteritems():
        formats = copy.copy(value)
        datas = add_data(formats, rel_format_formats, rel_format_data, list_edam_data=[])
        datas_v = [{'uri':data_item,'term':term_labels.get(data_item,'')} for data_item in datas]
        formats_v = [{'uri':format_item,'term':term_labels.get(format_item,'')} for format_item in value]
        dict_map[key] = {'formats':formats_v, 'data':datas_v}
    return dict_map


def dict_to_yaml(mapping_dict, yamlfile):
    """
    :param mapping_dict:
    :param yamlfile:
    :return:
    """
    stream = file(yamlfile, 'w')
    yaml.dump(mapping_dict, stream, default_flow_style=False)


def galaxy_to_edamdict(url, key):
    """
    :param url:
    :param key:
    :return:
    """
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

def run():
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
        config = regate.Config(args.config_file, "remag")
        dict_mapping = galaxy_to_edamdict(config.galaxy_url_api, config.api_key)
        relation_format_formats, relation_format_data, term_labels = edam_to_dict(config.edam_file)
        yaml_file = config.output_yaml
        dict_mapping = add_datas(dict_mapping, relation_format_formats, relation_format_data, term_labels)
        dict_to_yaml(dict_mapping, yaml_file)
    elif args.templateconfig:
        regate.generate_template()
    else:
        parser.print_help()
