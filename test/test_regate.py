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

    def test_build_tool_name(self):
        tool_id = u"galaxy.web.pasteur.fr/toolshed-pasteur/repos/fmareuil/fqconvert2/fqconvert/1.0.0"
        tool_version = u"1.0.0"
        self.assertEqual(build_tool_name(tool_id, tool_version),"galaxy_web_pasteur_fr_toolshed-pasteur_repos_fmareuil_fqconvert2_fqconvert_1_0_0")
        tool_id = u"fqconvert"
        tool_version = u"1.0.0"
        self.assertEqual(build_tool_name(tool_id, tool_version),"fqconvert_1_0_0")

if __name__ == '__main__':
    unittest.main()