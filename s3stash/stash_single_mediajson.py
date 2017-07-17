#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys, os
import argparse
import logging
import json
from s3stash.nxstash_mediajson import NuxeoStashMediaJson

def main(argv=None):

    parser = argparse.ArgumentParser(
        description='Create and stash media.json file for a nuxeo object')
    parser.add_argument('path', help="Nuxeo document path")
    parser.add_argument(
        '--bucket',
        default='static.ucldc.cdlib.org/media_json',
        help="S3 bucket name")
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument(
        '--pynuxrc', default='~/.pynuxrc', help="rc file for use by pynux")
    if argv is None:
        argv = parser.parse_args()

    # logging
    # FIXME would like to name log with nuxeo UID
    filename = os.path.basename(argv.path)
    logfile = "logs/mediajson-{}.log".format(filename)
    print "LOG:\t{}".format(logfile)
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)

    # create and stash media.json 
    nxstash = NuxeoStashMediaJson(
        argv.path,
        argv.bucket,
        argv.region,
        argv.pynuxrc,
        True)
    report = nxstash.nxstashref()

    # output report to json file
    reportfile = "reports/mediajson-{}.json".format(filename)
    with open(reportfile, 'w') as f:
        json.dump(report, f, sort_keys=True, indent=4)

    # parse report to give basic stats
    print "REPORT:\t{}".format(reportfile)
    print "SUMMARY:"
    print "stashed:\t{}".format(report['stashed'])

    print "\nDone."


if __name__ == "__main__":
    sys.exit(main())
