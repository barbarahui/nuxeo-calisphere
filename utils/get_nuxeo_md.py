#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import argparse
from pynux import utils
import pprint
pp = pprint.PrettyPrinter(indent=4)
import json

def main(argv=None):

    parser = argparse.ArgumentParser(
        description='Print nuxeo json metadata for object.')
    parser.add_argument('path', help="Nuxeo document path")

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()

    path = argv.path

    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())
    uid = nx.get_uid(path)
    metadata = nx.get_metadata(uid=uid)

    json_metadata = json.dumps(metadata, sort_keys=True, indent=4)

    print(json_metadata)

if __name__ == "__main__":
    sys.exit(main())
