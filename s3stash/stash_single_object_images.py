#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys, os
import argparse
import logging
import json
from s3stash.nxstashref_image import NuxeoStashImage
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
from pynux import utils

def main(argv=None):

    parser = argparse.ArgumentParser(
        description='For object, including components, produce jp2 version of any Nuxeo image files and stash on S3.')
    parser.add_argument('path', help="Nuxeo document path")
    parser.add_argument(
        '--bucket',
        default='ucldc-private-files/jp2000',
        help="S3 bucket name")
    parser.add_argument('--region', default='us-west-2', help='AWS region')
    parser.add_argument(
        '--pynuxrc', default='~/.pynuxrc', help="rc file for use by pynux")
    parser.add_argument(
        '--replace',
        action="store_true",
        help="replace file on s3 if it already exists")
    if argv is None:
        argv = parser.parse_args()

    # logging
    # FIXME would like to name log with nuxeo UID
    filename = os.path.basename(argv.path)
    logfile = "logs/{}.log".format(filename)
    print "LOG:\t{}".format(logfile)
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)


    nx = utils.Nuxeo(rcfile=open(os.path.expanduser(argv.pynuxrc), 'r'))
    dh = DeepHarvestNuxeo(argv.path, argv.bucket, pynuxrc=argv.pynuxrc)

    report = {}
    # convert and stash parent jp2 
    nxstash = NuxeoStashImage(unicode(argv.path, "utf-8"), argv.bucket, argv.region,
                              argv.pynuxrc, argv.replace)
    report[nxstash.uid] = nxstash.nxstashref()

    # stash component jp2s
    obj = nx.get_metadata(path=argv.path)
    for c in dh.fetch_components(obj):
        nxstash = NuxeoStashImage(c['path'], argv.bucket, argv.region,
                                      argv.pynuxrc, argv.replace)
        report[nxstash.uid] = nxstash.nxstashref()

    # output report to json file
    reportfile = "reports/{}.json".format(filename)
    with open(reportfile, 'w') as f:
        json.dump(report, f, sort_keys=True, indent=4)

    # parse report to give basic stats
    report = json.load(open(reportfile))
    print "REPORT:\t{}".format(reportfile)
    print "SUMMARY:"
    print "processed:\t{}".format(len(report))
    not_image = len([
        key for key, value in report.iteritems()
        if not value['is_image']['is_image']
    ])
    print "not image:\t{}".format(not_image)
    unrecognized = len([
        key for key, value in report.iteritems()
        if not value['precheck']['pass']
    ])
    print "not convertible:\t{}".format(unrecognized)
    converted = len(
        [key for key, value in report.iteritems() if value['converted']])
    already_stashed = len([
        key for key, value in report.iteritems()
        if 'already_s3_stashed' in value.keys() and value['already_s3_stashed']
    ])
    print "converted:\t{}".format(converted)
    stashed = len(
        [key for key, value in report.iteritems() if value['stashed']])
    print "stashed:\t{}".format(stashed)

    print "\nDone."


if __name__ == "__main__":
    sys.exit(main())
