#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import argparse
import logging
import json
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
from s3stash.nxstashref_file import NuxeoStashFile

VALID_CALISPHERE_TYPES = ['file', 'audio', 'video']

def main(argv=None):
    ''' stash Nuxeo files of type 'file', 'audio', or 'video' for a collection '''
    parser = argparse.ArgumentParser(description='For Nuxeo collection, stash files (pdf, txt, etc) in S3.')
    parser.add_argument('path', help="Nuxeo document path to collection")
    parser.add_argument('--bucket', default='ucldc-nuxeo-ref-media', help="S3 bucket name")
    parser.add_argument('--region', default='us-west-2', help="aws region")
    parser.add_argument('--pynuxrc', default='~/.pynuxrc', help="rc file for use by pynux")
    parser.add_argument('--replace', action="store_true", help="replace file on s3 if it already exists")
    if argv is None:
        argv = parser.parse_args()

    collection = argv.path.split('/')[-1]

    # logging
    logfile = 'logs/{}.log'.format(collection)
    print "LOG:\t{}".format(logfile)
    logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)
 
    dh = DeepHarvestNuxeo(argv.path, argv.bucket, pynuxrc=argv.pynuxrc)

    report = {}

    objects = dh.fetch_objects()
    for obj in objects:
        nxstash = NuxeoStashFile(obj['path'], argv.bucket, argv.region, argv.pynuxrc, argv.replace)
        report[nxstash.uid] = nxstash.nxstashref()
        for c in dh.fetch_components(obj):
            nxstash = NuxeoStashFile(c['path'], argv.bucket, argv.region, argv.pynuxrc, argv.replace) 
            report[nxstash.uid] = nxstash.nxstashref()

    # output report to json file
    reportfile = "reports/{}.json".format(collection)
    with open(reportfile, 'w') as f:
        json.dump(report, f, sort_keys=True, indent=4)

    # parse report to give basic stats
    report = json.load(open(reportfile))
    print "REPORT:\t{}".format(reportfile)
    print "SUMMARY:"
    print "processed:\t{}".format(len(report))
    not_file = len([key for key, value in report.iteritems() if not value['calisphere_type'] in VALID_CALISPHERE_TYPES])
    print "not type `file`, `audio` or `video`:\t{}".format(not_file)
    stashed = len([key for key, value in report.iteritems() if value['stashed']])
    print "stashed:\t{}".format(stashed)

    print "\nDone."

if __name__ == "__main__":
    sys.exit(main())
         
