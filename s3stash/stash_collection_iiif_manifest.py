#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import unicode_literals

import sys
import argparse
import logging
import json
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
from s3stash.nxstash_iiif_manifest import NuxeoStashIIIFManifest


def main(argv=None):
    ''' create and stash media.json files for a nuxeo collection '''

    parser = argparse.ArgumentParser(description='Create and stash IIIF manifest '
                                     'files for a nuxeo collection')
    parser.add_argument("path", help="Nuxeo document path")
    parser.add_argument("--bucket",
                        default="static.ucldc.cdlib.org/iiif_manifests",
                        help="S3 bucket where manifest files will be stashed")
    parser.add_argument('--region', default='us-east-1', help="aws region")
    parser.add_argument("--pynuxrc", default='~/.pynuxrc',
                        help="rc file for use by pynux")

    if argv is None:
        argv = parser.parse_args()

    collection = argv.path.split('/')[-1]

    # logging
    logfile = 'logs/iiifmanifest-{}.log'.format(collection)
    print "LOG:\t{}".format(logfile)
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)

    dh = DeepHarvestNuxeo(argv.path, argv.bucket, pynuxrc=argv.pynuxrc)

    report = {}

    objects = dh.fetch_objects()
    for obj in objects:
        nxstash = NuxeoStashIIIFManifest(
            obj['path'],
            argv.bucket,
            argv.region,
            argv.pynuxrc,
            True)
        report[nxstash.uid] = nxstash.nxstashref()

    # output report to json file
    reportfile = "reports/iiifmanifest-{}.json".format(collection)
    with open(reportfile, 'w') as f:
        json.dump(report, f, sort_keys=True, indent=4)

    # parse report to give basic stats
    report = json.load(open(reportfile))
    print "REPORT:\t{}".format(reportfile)
    print "SUMMARY:"
    print "processed:\t{}".format(len(report))

if __name__ == "__main__":
    sys.exit(main())
