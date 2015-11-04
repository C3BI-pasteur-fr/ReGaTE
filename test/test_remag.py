from bin.remag import *
import unittest


class TestRemag(unittest.TestCase):
    def test_return_formatted_edam(self):
        edam = "format_2333"
        result = return_formatted_edam(edam)
        self.assertEqual(result, "EDAM_format:2333")
        edam = "data_2333"
        result = return_formatted_edam(edam)
        self.assertEqual(result, "EDAM_data:2333")

    def test_is_true(self):
        value = "True"
        result = is_true(value)
        self.assertEqual(result, True)
        value = "true"
        result = is_true(value)
        self.assertEqual(result, True)
        value = "False"
        result = is_true(value)
        self.assertEqual(result, False)
        value = "anything"
        self.assertEqual(result, False)

    def test_http_to_edamform(self):
        url = "http://edamontology.org/data_0006"
        result = http_to_edamform(url)
        self.assertEqual(result, "EDAM_data:0006")
        url = "http://edamontology.org/format_1915"
        result = http_to_edamform(url)
        self.assertEqual(result, "EDAM_format:1915")

    def test_add_datas(self):
        dict_map = {'fastqsanger': ['EDAM_format:1932'], 'pileup': ['EDAM_format:3015'], 'pir': ['EDAM_format:2330']}
        relation_format_formats = {'EDAM_format:1932': ['EDAM_format:2182'],'EDAM_format:3015': ['EDAM_format:2330',
                                   'EDAM_format:2920'], 'EDAM_format:2330': ['EDAM_format:1915'],
                                   'EDAM_format:2182': ['EDAM_format:2330', 'EDAM_format:2545'],
                                   'EDAM_format:2545': ['EDAM_format:2057'], 'EDAM_format:2057': ['EDAM_format:1919'],
                                   'EDAM_format:1919': ['EDAM_format:2350'],'EDAM_format:2350': ['EDAM_format:1915']}
        relation_format_data = {'EDAM_format:2920': 'EDAM_data:1381', 'EDAM_format:1919': 'EDAM_data:0849',
                                'EDAM_format:2057': 'EDAM_data:0924'}
        result = add_datas(dict_map, relation_format_formats, relation_format_data)
        self.assertEqual(result, {'fastqsanger': ['EDAM_format:1932', 'EDAM_data:0006', 'EDAM_data:0924'],
                                 'pileup': ['EDAM_format:3015', 'EDAM_data:1381', 'EDAM_data:0006'],
                                 'pir': ['EDAM_format:2330', 'EDAM_data:0006']})

if __name__ == '__main__':
    unittest.main()