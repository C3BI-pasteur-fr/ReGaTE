from regate import *
import unittest


class TestRegate(unittest.TestCase):
    def test_clean_dict(self):
        #dico = {"key1":"value1","key2":"","key3":[{"key1":"value1", "key2":""},{"key2":[{"key1":"value1", "key2":""},{"key2":""}]},{[],[]}]}
        dico = {"key1":"value1","key2":"","key3":[]}
        result = clean_dict(dico)
        self.assertEqual(result, {"key1":"value1"})
        #self.assertEqual(result, {"key1":"value1","key3":[{"key1":"value1"},{"key2":[{"key1":"value1"}]}]})

if __name__ == '__main__':
    unittest.main()