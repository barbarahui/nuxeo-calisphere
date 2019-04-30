#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys, os
import argparse
import logging
import json
import boto
from s3stash.stash_collection import Stash as StashCollection
from s3stash.publish_to_harvesting import publish_to_harvesting

IMAGE_BUCKET = 'ucldc-private-files/jp2000'
IMAGE_REGION = 'us-west-2'
FILE_BUCKET = 'ucldc-nuxeo-ref-media'
FILE_REGION = 'us-west-2'
THUMB_BUCKET = 'static.ucldc.cdlib.org/ucldc-nuxeo-thumb-media'
THUMB_REGION = 'us-east-1'
MEDIAJSON_BUCKET = 'static.ucldc.cdlib.org/media_json'
MEDIAJSON_REGION = 'us-east-1'
REPORT_BUCKET = 'static.ucldc.cdlib.org/deep-harvesting/reports'

_loglevel_ = 'INFO'

class Stash(StashCollection):
    '''
        stash various files on s3 for a single nuxeo object
        including any components if complex
    '''
    def __init__(self, path, pynuxrc, replace=False, loglevel=_loglevel_):
        super(Stash, self).__init__(path, pynuxrc, replace, loglevel)

        self.logger = logging.getLogger(__name__)

    def fetch_objects(self):
        ''' fetch object to process '''
        metadata = self.dh.nx.get_metadata(path=self.path) 
        return [metadata]

def s3_report(report_file, report):
    '''Save s3 report'''
    S3_conn = boto.connect_s3()
    S3_bucket = S3_conn.get_bucket(REPORT_BUCKET)
    report_key = boto.s3.key.Key(S3_bucket)
    report_key.key = report_file
    # TODO: set type to application/json
    report_key.set_contents_from_string(
        json.dumps(report, sort_keys=True, indent=4)
    )

def main(path, pynuxrc="~/.pynuxrc", replace=True):

    # logging
    # FIXME would like to name log with nuxeo UID
    filename = os.path.basename(path)
    logfile = "logs/{}.log".format(filename)
    print "LOG:\t{}".format(logfile)
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)

    stash = Stash(path, pynuxrc, replace)
 
    filename = os.path.basename(path)

    # stash images for use with iiif server
    print 'stashing images...'
    image_report = stash.images()
    info = 'finished stashing images'
    logger.info(info)
    print info
    report_file = "images-{}.json".format(filename)
    s3_report(report_file, image_report)
    print "report:\t{}\n".format(report_file)

    # stash text, audio, video
    print 'stashing non-image files (text, audio, video)...'
    file_report = stash.files()
    info = 'finished stashing files'
    logger.info(info)
    print info
    report_file = "files-{}.json".format(filename)
    s3_report(report_file, file_report)
    print "report:\t{}\n".format(report_file)

    # stash thumbnails for text, audio, video
    print 'stashing thumbnails for non-image files (text, audio, video)...'
    thumb_report = stash.thumbnails()
    info = 'finished stashing thumbnails'
    logger.info(info)
    print info
    report_file = "thumbs-{}.json".format(filename)
    s3_report(report_file, thumb_report)
    print "report:\t{}\n".format(report_file)

    # stash media.json files
    print 'stashing media.json files for collection...'
    mediajson_report = stash.media_json()
    info = 'finished stashing media.json'
    logger.info(info)
    print info
    report_file = "mediajson-{}.json".format(filename)
    s3_report(report_file, mediajson_report)
    print "report:\t{}\n".format(report_file)

    # print some information about how it went
    images_stashed = len(
        [key for key, value in image_report.iteritems() if value['stashed']])
    files_stashed = len(
        [key for key, value in file_report.iteritems() if value['stashed']])
    thumbs_stashed = len(
        [key for key, value in thumb_report.iteritems() if value['stashed']])
    mediajson_stashed = len([
        key for key, value in mediajson_report.iteritems() if value['stashed']
    ])

    # TODO: make sure this is in rqworker log
    summary = ''.join((
        "SUMMARY:\n",
        "objects processed:              {}\n".format(len(stash.objects)),
        "replaced existing files on s3:  {}\n".format(stash.replace),
        "images stashed:                 {}\n".format(images_stashed),
        "files stashed:                  {}\n".format(files_stashed),
        "thumbnails stashed:             {}\n".format(thumbs_stashed),
        "media.json files stashed:       {}\n".format(mediajson_stashed),
        )
    )
    print summary
    publish_to_harvesting('Deep Harvest for {} done'.format(path),
                          summary)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='deep harvest nuxeo object, including components')
    parser.add_argument('path', help="Nuxeo document path")
    parser.add_argument(
        '--pynuxrc', default='~/.pynuxrc', help="rc file for use by pynux")
    parser.add_argument(
        '--replace',
        action="store_true",
        help="replace files on s3 if they already exist")
    
    argv = parser.parse_args()    

    path = argv.path
    pynuxrc = argv.pynuxrc
    replace = argv.replace

    sys.exit(
        main(
            path, pynuxrc=pynuxrc, replace=replace))
