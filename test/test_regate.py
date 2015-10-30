from bin.regate import *
import unittest


class TestRegate(unittest.TestCase):
    def test_newclean_dict(self):
        dico = {"key1":"value1","key2":"","key3":[],"key4":{"key2":""},"key5":{"key2":"mavalue"},"key6":[{"key1":"345"},
                {"key2":"","key4":""}],"key7":{"key2":{"key2":{}}},"key8":[{u'uri': "", u'term' : ""},
                {u'uri': "", u'term' : ""}],"key9":[{u'uri': "", u'term' : ""},{u'uri': "tempoaraire", u'term' : ""},{}]}
        clean_dict(dico)
        self.assertEqual(dico, {"key1":"value1","key5":{"key2":"mavalue"},"key6":[{"key1":"345"}],
                                "key9":[{u'uri': "tempoaraire"}]})

if __name__ == '__main__':
    unittest.main()