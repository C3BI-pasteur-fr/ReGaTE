# -*- coding: utf-8 -*-

"""
Created on Feb.2nd , 2015

@author: Olivia Doppelt-Azeroual, CIB-C3BI, Institut Pasteur, Paris
@author: Fabien Mareuil, CIB-C3BI, Institut Pasteur, Paris
@contact: olivia.doppelt@pasteur.fr
@project: ReGaTE
@githuborganization: bioinfo-center-pasteur-fr
@inspired by Herve Menager's 'mobyle1_to_btr.py
"""

import argparse
import requests
import getpass
import json
import os
import pprint


def auth(login):
    password = getpass.getpass()
    response = requests.post("https://elixir-registry.cbs.dtu.dk/api/auth/login",
                             '{"username": "%s", "password": "%s"}' % (login, password),
                             headers={'Accept': 'application/json', 'Content-type': 'application/json'}).text
    return json.loads(response)['token']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="import JSON to ELIXIR bioregistry")
    parser.add_argument("--login", help="registry login")
    parser.add_argument("--json_dir", help="directory for the json to import")
    args = parser.parse_args()

    if args.login:
        print "authenticating..."
        token = auth(args.login)
        print "authentication ok"
        ok_cnt = 0
        ko_cnt = 0
        print "attempting to delete all registered services..."
        resp = requests.delete('https://elixir-registry.cbs.dtu.dk/api/tool/%s' % args.login,
                               headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                        'Authorization': 'Token %s' % token})
        print resp
        print resp.headers
        print resp.status_code
        pprint.pprint(resp)

    if args.login and args.json_dir:
        print "loading json"
        print os.getcwd()
        path = os.path.join(os.getcwd(), args.json_dir)
        for jsonfile in os.listdir(args.json_dir):
            print jsonfile
            with open(os.path.join(path, jsonfile), 'r') as json_file:
                json_data = json.load(json_file)
                resp = requests.post('https://elixir-registry.cbs.dtu.dk/api/tool', json.dumps(json_data),
                                     headers={'Accept': 'application/json', 'Content-type': 'application/json',
                                              'Authorization': 'Token %s' % token})
                if resp.status_code == 201:
                    print "%s ok" % file
                    ok_cnt += 1
                else:
                    print "%s ko, error: %s" % (file, resp.text)
                    ko_cnt += 1
        print "afterFor"
    if args.login:
        print "import finished, ok=%s, ko=%s" % (ok_cnt, ko_cnt)
