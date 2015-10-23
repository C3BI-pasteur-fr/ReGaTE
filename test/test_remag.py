from remag import *
import unittest


class TestRemag(unittest.TestCase):
    def test_return_formatted_edam(self):
        edam = "format_2333"
        result = return_formatted_edam(edam)
        self.assertEqual(result, "EDAM_format:2333")
        edam = "data_2333"
        result = return_formatted_edam(edam)
        self.assertEqual(result, "EDAM_data:2333")

if __name__ == '__main__':
    unittest.main()