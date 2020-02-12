#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import argparse
import pprint
from s3stash.nxstashref import NuxeoStashRef
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
import s3stash.s3tools
from ucldc_iiif.convert import Convert
#import json


def main(argv=None):

    parser = argparse.ArgumentParser(
        description='list objects for a given collection where nuxeo doc type is image but file type is pdf')
    parser.add_argument('registry_id', help='UCLDC Registry ID')
    parser.add_argument(
        '--pynuxrc',
        default='~/.pynuxrc-basic',
        help="rcfile for use with pynux utils")
    if argv is None:
        argv = parser.parse_args()

    registry_id = argv.registry_id

    # get nuxeo path
    nxpath = s3stash.s3tools.get_nuxeo_path(registry_id)
    if nxpath is None:
        print "No record found for registry_id: {}".format(registry_id)
        sys.exit()

    dh = DeepHarvestNuxeo(nxpath, '', pynuxrc=argv.pynuxrc)
    print "about to fetch objects for path {}".format(dh.path)
    objects = dh.fetch_objects()
    object_count = len(objects)
    print "finished fetching objects. {} found".format(object_count)

    convert = Convert()
    counter = 0
    for obj in objects:
        if dh.has_file(obj) and obj['type'] == u'SampleCustomPicture' and obj['properties']['file:content']['mime-type'] == u'application/pdf':
            print obj['uid'], obj['path'], obj['type'], obj['properties']['file:content']['name']
            counter = counter + 1    

    print counter

if __name__ == "__main__":
    sys.exit(main())
