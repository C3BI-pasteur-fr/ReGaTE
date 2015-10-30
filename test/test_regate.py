from bin.regate import *
import unittest


class TestRegate(unittest.TestCase):
    def test_clean_dict(self):
        #dico = {"key1":"value1","key2":"","key3":[{"key1":"value1", "key2":""},{"key2":[{"key1":"value1", "key2":""},{"key2":""}]},{[],[]}]}
        #dico = {"key1":"value1","key2":"","key3":[],"key4":{"key2":""},"key5":{"key2":"mavalue"},"key6":[{"key1":"345"},{"key2":"","key4":""}],"key7":{"key2":{"key2":{}}},"key8":[{u'uri': "", u'term' : ""},{u'uri': "", u'term' : ""}],
        #        "key9":[{u'uri': "", u'term' : ""},{u'uri': "tempoaraire", u'term' : ""},{}]}
        #dico = {"key9":[{u'uri': "", u'term' : [{u'uri': "", u'term' : ""},{u'uri': "tempoaraire", u'term' : [{u'uri': "", u'term' : ""},{u'uri': "tempoaraire", u'term' : ""}]}]},{u'uri': "tempoaraire", u'term' : ""}]}
        dico= {
    "accessibility": "private",
    "version": "1.1",
    "homepage": "https://galaxy.web.pasteur.fr",
    "function": [
        {
            "output": [
                {
                    "dataType": {
                        "term": "EDAM label placeholder",
                        "uri": "http://edamontology.org/data_0006"
                    },
                    "dataHandle": "",
                    "dataFormat": [
                        {
                            "term": "EDAM label placeholder",
                            "uri": "http://edamontology.org/format_1915"
                        }
                    ],
                    "dataDescription": ""
                }
            ],
            "functionName": [],
            "functionHandle": "MainFunction",
            "functionDescription": "Soap aligner index maker.",
            "input": [
                {
                    "dataType": {
                        "term": "EDAM label placeholder",
                        "uri": "http://edamontology.org/data_0006"
                    },
                    "dataHandle": "fasta",
                    "dataFormat": [
                        {
                            "term": "EDAM label placeholder",
                            "uri": "http://edamontology.org/format_1929"
                        }
                    ],
                    "dataDescription": ""
                }
            ]
        }
    ],
    "description": "Soap aligner index maker.",
    "collection": [
        "Galaxy@pasteur"
    ],
    "uses": [
        {
            "usesHomepage": "https://galaxyapi.web.pasteur.fr",
            "usesName": "galaxy.web.pasteur.fr/toolshed-pasteur/repos/odoppelt/soap/2bwt-builder/1.1",
            "usesVersion": "1.1"
        }
    ],
    "interface": [
        {
            "interfaceDocs": "",
            "interfaceType": "WEB UI",
            "interfaceSpecFormat": "",
            "interfaceSpecURL": ""
        }
    ],
    "sourceRegistry": "https://galaxy.web.pasteur.fr/toolshed-pasteur/repos/odoppelt/soap",
    "name": "2bwt-builder",
    "resourceType": [
        "Tool"
    ],
    "maturity": "Established",
    "contact": [
        {
            "contactEmail": "galaxy@pasteur.fr",
            "contactTel": "",
            "contactURL": "",
            "contactName": "Institut Pasteur galaxy team",
            "contactRole": []
        }
    ],
    "publications": {
        "publicationsPrimaryID": "None"
    }
}
        clean_dict(dico)
        #lf.assertEqual(dico, {"key1":"value1","key5":{"key2":"mavalue"},"key6":[{"key1":"345"}], "key9":[{u'uri': "tempoaraire"}]})
        #self.assertEqual(dico, {"key9":[{ u'term' : [{u'uri': "tempoaraire", u'term' : [{u'uri': "tempoaraire"}]}]},{u'uri': "tempoaraire"}]})
        self.assertEqual(dico, {"accessibility": "private",
    "version": "1.1",
    "homepage": "https://galaxy.web.pasteur.fr",
    "function": [
        {
            "output": [
                {
                    "dataType": {
                        "term": "EDAM label placeholder",
                        "uri": "http://edamontology.org/data_0006"
                    },
                    "dataFormat": [
                        {
                            "term": "EDAM label placeholder",
                            "uri": "http://edamontology.org/format_1915"
                        }
                    ],
                }
            ],
            "functionHandle": "MainFunction",
            "functionDescription": "Soap aligner index maker.",
            "input": [
                {
                    "dataType": {
                        "term": "EDAM label placeholder",
                        "uri": "http://edamontology.org/data_0006"
                    },
                    "dataHandle": "fasta",
                    "dataFormat": [
                        {
                            "term": "EDAM label placeholder",
                            "uri": "http://edamontology.org/format_1929"
                        }
                    ],
                }
            ]
        }
    ],
    "description": "Soap aligner index maker.",
    "collection": [
        "Galaxy@pasteur"
    ],
    "uses": [
        {
            "usesHomepage": "https://galaxyapi.web.pasteur.fr",
            "usesName": "galaxy.web.pasteur.fr/toolshed-pasteur/repos/odoppelt/soap/2bwt-builder/1.1",
            "usesVersion": "1.1"
        }
    ],
    "interface": [
        {
            "interfaceType": "WEB UI",
        }
    ],
    "sourceRegistry": "https://galaxy.web.pasteur.fr/toolshed-pasteur/repos/odoppelt/soap",
    "name": "2bwt-builder",
    "resourceType": [
        "Tool"
    ],
    "maturity": "Established",
    "contact": [
        {
            "contactEmail": "galaxy@pasteur.fr",
            "contactName": "Institut Pasteur galaxy team",
        }
    ],
    "publications": {
        "publicationsPrimaryID": "None"
    }
})

        #self.assertEqual(result, {"key1":"value1","key3":[{"key1":"value1"},{"key2":[{"key1":"value1"}]}]})

if __name__ == '__main__':
    unittest.main()