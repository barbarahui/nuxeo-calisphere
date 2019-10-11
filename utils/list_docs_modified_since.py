#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import argparse
from datetime import datetime
from dateutil.parser import parse
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo

def main(argv=None):

    parser = argparse.ArgumentParser(
        description='Print count of objects for a given collection.')
    parser.add_argument('path', help="Nuxeo path to collection")
    parser.add_argument('since_date', help="Script will list docs updated since midnight on this date, GMT. Format YYYY-MM-DD", type=valid_date)
    parser.add_argument(
        '--pynuxrc',
        default='~/.pynuxrc',
        help="rcfile for use with pynux utils")
    parser.add_argument(
        '--components',
        action='store_true',
        help="show counts for object components")
    if argv is None:
        argv = parser.parse_args()

    dh = DeepHarvestNuxeo(argv.path, '', pynuxrc=argv.pynuxrc)
    print "about to fetch docs for path {}".format(dh.path)
    objects = dh.fetch_objects()

    component_count = 0
    for obj in objects:
       last_mod_str = obj['lastModified'][:10]
       last_mod_date = parse(last_mod_str)
       if last_mod_date > argv.since_date:
           print last_mod_str, obj['path']

       '''
       components = dh.fetch_components(obj)
       for c in components:
           last_mod_str = c['lastModified'][:10]
           last_mod_date = parse(last_mod_str)
           if last_mod_date > argv.since_date:
               print last_mod_str, obj['path']
       '''

def valid_date(string):
    try:
        return datetime.strptime(string, '%Y-%m-%d')
    except ValueError:
        msg = "Not a valid date: '{}'.".format(string)
        raise argparse.ArgumentTypeError(msg)

if __name__ == "__main__":
    sys.exit(main())
