#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
from pynux import utils 

def main(argv=None):

    parser = argparse.ArgumentParser(description='Print nuxeo path for given uid.')
    parser.add_argument('uid', help="Nuxeo uid")

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()
    
    uid = argv.uid

    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())
    metadata = nx.get_metadata(uid=uid)
    path = metadata['path']
    print path, uid 

if __name__ == "__main__":
    sys.exit(main())
