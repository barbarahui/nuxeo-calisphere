#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import argparse
import couchdb
import ssl
import s3stash.s3tools
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo

def main(argv=None):
    parser = argparse.ArgumentParser(
        description='print differences between Nuxeo and CouchDB for a '
                    'given collection'
    )
    parser.add_argument('regid', help="Collection Registry ID")
    parser.add_argument(
        '--pynuxrc',
        default='~/.pynuxrc-basic',
        help="rcfile for use with pynux utils")

    if argv is None:
        argv = parser.parse_args()

    registry_id = argv.regid
    couch = get_couch_objects(registry_id)
    print('couch has {} objects'.format(len(couch)))

    nxpath = s3stash.s3tools.get_nuxeo_path(registry_id)
    if nxpath is None:
        print "No record found for registry_id: {}".format(registry_id)
        sys.exit()

    dh = DeepHarvestNuxeo(nxpath, '', pynuxrc=argv.pynuxrc)
    print "about to fetch objects for path {}".format(dh.path)
    for obj in dh.fetch_objects():
        incouch = True if obj['uid'] in couch else False
        if not incouch:
            print(obj['uid'])

def get_nx_objects(path):
    print "getting Nuxeo objects for {}".format(path)


def get_couch_objects(id):
    print "getting couchDB objects for collection ID {}".format(id)
    ssl._create_default_https_context = ssl._create_unverified_context # FIXME bad.
    couch = couchdb.Server('https://harvest-stg.cdlib.org/couchdb')
    db = couch['ucldc']
    return [row.id.split('--')[1] for row in db.view('all_provider_docs/by_provider_name_wdoc', key=id)]

if __name__ == "__main__":
    sys.exit(main())
