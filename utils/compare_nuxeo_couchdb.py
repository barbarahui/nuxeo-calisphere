#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import argparse
import s3stash.s3tools
import requests
import json
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo

def main(argv=None):

    parser = argparse.ArgumentParser(
        description='Print info on objects missing from couchdb for Nuxeo collection')
    parser.add_argument('id', help='Collection registry ID')
    parser.add_argument(
        '--pynuxrc',
        default='~/.pynuxrc',
        help="rcfile for use with pynux utils")
    if argv is None:
        argv = parser.parse_args()

    registry_id = argv.id
    print "Registry ID: {}".format(registry_id)

    nxpath = s3stash.s3tools.get_nuxeo_path(registry_id)
    print "Nuxeo path: {}".format(nxpath)

    # get couchdb data
    view = "https://harvest-stg.cdlib.org/couchdb/ucldc/_design/all_provider_docs/_view/by_provider_name?key=%22{}%22".format(registry_id)
    print view
    res = requests.get(view, verify=False) # FIXME we want to verify
    res.raise_for_status()
    couchdata = json.loads(res.content)
    rows = couchdata['rows']
    delimiter = "{}--".format(registry_id)
    couch_uids = [row['id'].split(delimiter)[1] for row in rows]
    couch_count = len(couch_uids)
    print "Total rows in couchdb: {}".format(couch_count)

    # get nuxeo data
    dh = DeepHarvestNuxeo(nxpath, '', pynuxrc=argv.pynuxrc)
    print "about to fetch objects for path {}".format(dh.path)
    objects = dh.fetch_objects()
    nx_count = len(objects)
    print "Total objects in Nuxeo: {}".format(nx_count)

    for obj in objects:
        if obj['uid'] not in couch_uids:
            print obj['uid'], obj['path']
 
if __name__ == "__main__":
    sys.exit(main())
