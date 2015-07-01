#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo

def main(argv=None):

    parser = argparse.ArgumentParser(description='Print count of objects for a given collection.')
    parser.add_argument('path', help="Nuxeo path to collection")
    parser.add_argument('--pynuxrc', default='~/.pynuxrc-prod', help="rcfile for use with pynux utils")
    if argv is None:
        argv = parser.parse_args()
    
    dh = DeepHarvestNuxeo(argv.path, 'barbarahui_test_bucket', argv.pynuxrc)
    print "about to fetch objects for path {}".format(dh.path)
    objects = dh.fetch_objects()
    print "finished" 
    print "len(objects): {}".format(len(objects))

if __name__ == "__main__":
    sys.exit(main())
