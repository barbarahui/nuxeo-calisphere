#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
from pynux import utils
import couchdb
import ssl

def main(argv=None):
    parser = argparse.ArgumentParser(description='print differences between Nuxeo and CouchDB for a given collection')
    parser.add_argument('path', help="Nuxeo document path for collection")
    parser.add_argument('regid', help="Collection Registry ID")

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()

    nuxeo = get_nx_objects(argv.path)
    couch = get_couch_objects(argv.regid)

def get_nx_objects(path):
    print "getting Nuxeo objects for {}".format(path)

def get_couch_objects(id):
    print "getting couchDB objects for collection ID {}".format(id)
    ssl._create_default_https_context = ssl._create_unverified_context
    couch = couchdb.Server('https://52.10.100.133/couchdb') 
    db = couch['ucldc']
    #map = '''function(doc) {
    #    if (collection_id = doc.id.split('--').shift() == '19'); emit(collection_id, doc)
    #}
    #'''
    #for row in db.query(map):
    #    print (row.key)

    
    for row in db.view('all_provider_docs/by_provider_name_wdoc'):
        print(row.id)
    #print db['76--08999aaf-03f9-4054-943e-24f66b2ac9fe']
    #view = '_design/all_provider_docs/_view/by_provider_name_wdoc?key=%22{}%22&field=originalRecord.identifier'.format(id)
    

if __name__ == "__main__":
    sys.exit(main())
