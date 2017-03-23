#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import argparse
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo


def main(argv=None):

    parser = argparse.ArgumentParser(
        description='Print count of objects for a given collection.')
    parser.add_argument('path', help="Nuxeo path to collection")
    parser.add_argument(
        '--pynuxrc',
        default='~/.pynuxrc-prod',
        help="rcfile for use with pynux utils")
    parser.add_argument(
        '--components',
        action='store_true',
        help="show counts for object components")
    if argv is None:
        argv = parser.parse_args()

    dh = DeepHarvestNuxeo(argv.path, '', pynuxrc=argv.pynuxrc)
    print "about to fetch objects for path {}".format(dh.path)
    objects = dh.fetch_objects()
    object_count = len(objects)
    print "finished fetching objects. {} found".format(object_count)

    if not argv.components:
        return

    print "about to iterate through objects and get components"
    component_count = 0
    for obj in objects:
        components = dh.fetch_components(obj)
        component_count = component_count + len(components)
    print "finished fetching components. {} found".format(component_count)
    print "Grand Total: {}".format(object_count + component_count)


if __name__ == "__main__":
    sys.exit(main())
