#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging
from s3stash.stash_collection import Stash

_loglevel_ = 'INFO'

def main(nxpath, pynuxrc="~/.pynuxrc", replace=True, loglevel=_loglevel_):
    # set up logging
    logfile = 'logs/stash_folder'
    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    # log to stdout/err to capture in parent process log
    # TODO: save log to S3
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        stream=sys.stderr)
    logger = logging.getLogger(__name__)

    stash = Stash(nxpath, pynuxrc, replace)

    # stash images for use with iiif server
    print 'stashing images...'
    image_report = stash.images()
    info = 'finished stashing images'
    logger.info(info)
    print info
    report_file = "images.json"
    print "report:\t{}\n".format(report_file)

    # stash text, audio, video
    print 'stashing non-image files (text, audio, video)...'
    file_report = stash.files()
    info = 'finished stashing files'
    logger.info(info)
    print info
    report_file = "files.json"
    print "report:\t{}\n".format(report_file)

    # stash thumbnails for text, audio, video
    print 'stashing thumbnails for non-image files (text, audio, video)...'
    thumb_report = stash.thumbnails()
    info = 'finished stashing thumbnails'
    logger.info(info)
    print info
    report_file = "thumbs.json"
    print "report:\t{}\n".format(report_file)

    # stash media.json files
    print 'stashing media.json files for collection...'
    mediajson_report = stash.media_json()
    info = 'finished stashing media.json'
    logger.info(info)
    print info
    report_file = "mediajson.json"
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Deep harvest objects in a given folder in nuxeo')
    parser.add_argument('path', help='nuxeo path')
    parser.add_argument(
        '--pynuxrc', default='~/.pynuxrc', help='rc file for use by pynux')
    parser.add_argument(
        '--replace',
        action='store_true',
        help='replace files on s3 if they already exist')
    parser.add_argument('--loglevel', default=_loglevel_)

    argv = parser.parse_args()

    path = argv.path
    pynuxrc = argv.pynuxrc
    replace = argv.replace
    loglevel = argv.loglevel

    sys.exit(
        main(
            path, pynuxrc=pynuxrc, replace=replace, loglevel=loglevel))
