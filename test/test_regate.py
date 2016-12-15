import unittest
import os
from glob import glob
import json

from nose_parameterized import parameterized
import ruamel.yaml

from regate.regate import map_tool, Config, build_edam_dict

def get_yml_list():
    tests = []
    yml_dir = os.path.dirname(__file__) 
    yml_list = glob(os.path.join(yml_dir,'*.yml'))
    for yml_path in yml_list:
        json_path = os.path.splitext(yml_path)[0] + '.json'
        tests.append([yml_path, json_path])
    return  tests

class TestRegate(unittest.TestCase):

    @parameterized.expand(get_yml_list())
    def test_map_tool(self, yml_path, json_path):
        self.maxDiff = None
        conf = Config(os.path.join(os.path.dirname(__file__),'conftest.ini'), 'regate')
        mapping_file = build_edam_dict(os.path.join(os.path.dirname(__file__),'mapping.yml.conf'))
        tool_yml = ruamel.yaml.load(open(yml_path, 'r'), Loader=ruamel.yaml.Loader)
        expected_tool_json = ruamel.yaml.load(open(json_path, 'r'), Loader=ruamel.yaml.Loader)
        test_tool_json = map_tool(tool_yml, conf, mapping_file)
        self.assertEqual(test_tool_json, expected_tool_json)

if __name__ == '__main__':
    unittest.main()
