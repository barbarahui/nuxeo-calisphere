#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
from pynux import utils 

def main(argv=None):

    parser = argparse.ArgumentParser(description='Print nuxeo json metadata for object.')
    parser.add_argument('path', help="Nuxeo document path")

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()
    
    path = argv.path

    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())
    uid = nx.get_uid(path)
    metadata = nx.get_metadata(uid=uid)
    

if __name__ == "__main__":
    sys.exit(main())
