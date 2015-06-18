#!/usr/bin/python
import string
import os
import yaml
import rdflib
import xml.etree.ElementTree as ET


def is_true(value):
    return value.lower() == "true"
 
def is_edamtype(dic_child):
    if 'edam' in dic_child:
        if dic_child['edam'] not in ['', "None", "Null"]:
            return True
        else:
            return False
    else:
        return False
    
def csv_to_dict(edam_mapping_file, mapping_dict):
    with open(edam_mapping_file, "r") as EG_MAPPING:
        for line in EG_MAPPING:
            splitted = string.split(line,'\t')
            if len(splitted) > 1 and splitted[0] not in ["GALAXY", "NAME", '"', "EXTENSION",'']:
                if splitted[3].strip() in ['']:
                    mapping_dict[splitted[0].strip()] =  ["Not Mapped Yet"]
                else:
                    mapping_dict[splitted[0].strip()] = [splitted[3].strip()]
    return mapping_dict
    
def csv_to_dict2(edam_mapping_file, mapping_dict):
    with open(edam_mapping_file, "r") as EG_MAPPING:
        for line in EG_MAPPING:
            splitted = string.split(line,'\t')
            if len(splitted) > 1 and splitted[0] not in ["GALAXY", "NAME", '"', "EXTENSION",'']:
                if splitted[1].strip() in ['']:
                    mapping_dict[splitted[0].strip()] =  ["Not Mapped Yet"]
                else:
                    form_edam = splitted[1].strip().split("_")
                    mapping_dict[splitted[0].strip()] = ["EDAM_{}:{:0>4d}".format(form_edam[0],int(form_edam[1]))]
    return mapping_dict

def return_formatted_edam(edam):
    edam = string.split(edam,'_')
    edam = "EDAM_{}:{:0>4d}".format(edam[0], int(edam[1]))
    return edam

def xml_to_dict(datatype_file_xml, mapping_dict):
    tree = ET.parse(datatype_file_xml)
    root = tree.getroot()
    for child in root[0]:
        if 'display_in_upload' in child.attrib:
            if is_edamtype(child.attrib):
                edam_format = return_formatted_edam(child.attrib['edam'])
                if not child.attrib['extension'] in mapping_dict and is_true(child.attrib['display_in_upload']):
                    mapping_dict[child.attrib['extension']] = [edam_format]
            else:
                if not child.attrib['extension'] in mapping_dict and is_true(child.attrib['display_in_upload']):
                    mapping_dict[child.attrib['extension']] = ["Not Mapped Yet"]                   
    return mapping_dict

def http_to_edamform(url):
    base = string.split(os.path.basename(url),'_')
    return str("EDAM_{}:{:0>4d}").format(base[0],int(base[1]))
    
def edam_to_dict(edam_file):
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
    Property={"oboInOwl":"http://www.geneontology.org/formats/oboInOwl#"}
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

def add_data(formats, relation_format_formats, relation_format_data, list_edam_data):
    if len(formats) != 0:
        for format in formats:
            if format in  relation_format_data:
                list_edam_data.append(relation_format_data[format])
                formats.remove(format)
                return add_data(formats, relation_format_formats, relation_format_data, list_edam_data)
            elif format in relation_format_formats:
                formats.remove(format)
                formats = formats + relation_format_formats[format]
                return add_data(formats, relation_format_formats, relation_format_data, list_edam_data)
            else:
                print "NO FORMAT AND NO DATA FOR %s" % format
                formats.remove(format)
                if format in ("Not Mapped Yet", "NONE Known"):
                    return add_data(formats, relation_format_formats, relation_format_data, list_edam_data)
                else: 
                    list_edam_data.append("EDAM_data:0006")
                    return add_data(formats, relation_format_formats, relation_format_data, list_edam_data)
    else:
        return list_edam_data
            
def add_datas(dict_map, relation_format_formats, relation_format_data):
    import copy
    for key, value in dict_map.iteritems():
        formats = copy.copy(value)
        datas = add_data(formats, relation_format_formats, relation_format_data, list_edam_data=[])
        dict_map[key] = value + datas                
    return dict_map

def dict_to_yaml(mapping_dict, yamlfile):
    stream = file(yamlfile, 'w')
    yaml.dump(mapping_dict, stream, default_flow_style=False)
    #print yaml.dump(mapping_dict, default_flow_style=False)

if __name__ == "__main__":
    dict_mapping = {}
    #edam_galaxy_file = "EDAM_GALAXY_MAPPING.tsv"
    edam_galaxy_file = "mapping"
    xml_datatype_file = "datatypes_edam_conf.xml"
    yaml_file = "yaml_mapping.yaml"
    relation_format_formats, relation_format_data = edam_to_dict("EDAM_1.9.owl")
    dict_mapping = csv_to_dict2(edam_galaxy_file, dict_mapping)
    dict_mapping = xml_to_dict(xml_datatype_file, dict_mapping)
    dict_mapping = add_datas(dict_mapping,relation_format_formats, relation_format_data)
    dict_to_yaml(dict_mapping, yaml_file)


