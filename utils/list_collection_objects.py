#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import argparse
import pprint
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
import s3stash.s3tools
import json

PER_PAGE = 100

def main(argv=None):

    parser = argparse.ArgumentParser(
        description='list objects for a given collection.')
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

    print "about to iterate through objects and get components"
    component_count = 0
    all_components = []
    for obj in objects:
        components = dh.fetch_components(obj) 
        all_components.extend(components)
        print "{} components for {}".format(len(components), obj['uid'])
    print "finished fetching components. {} found".format(len(all_components))

    objects.extend(components)
    total_obj = len(objects)
    print "Grand Total: {}".format(total_obj)

    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    chunks = [objects[i:i + PER_PAGE] for i in xrange(0, len(objects), PER_PAGE)]

    count = 0
    for c in chunks:
        count = count + 1        
        filepath = 'chunks/{}_{}.txt'.format(registry_id, count)
        print "Writing file: {}".format(filepath)
        with open(filepath, 'w') as f:
            json.dump(c, f, indent=4)

    ##pp = pprint.PrettyPrinter(indent=4)
    ##pp.pprint(chunks)


if __name__ == "__main__":
    sys.exit(main())
