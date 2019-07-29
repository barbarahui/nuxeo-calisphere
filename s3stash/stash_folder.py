#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys, os
import argparse
import logging
from s3stash.stash_collection import Stash as StashCollection
from s3stash.publish_to_harvesting import publish_to_harvesting

_loglevel_ = 'INFO'

class Stash(StashCollection):
    '''
       stash various files on s3 for a given nuxeo path
       including any components if complex
    '''
    def __init__(self, path, pynuxrc, replace=False, loglevel=_loglevel_):
        super(Stash, self).__init__(path, pynuxrc, replace, loglevel)

        self.logger = logging.getLogger(__name__)

def main(path, pynuxrc="~/.pynuxrc", replace=True, loglevel=_loglevel_):
    # set up logging
    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    # log to stdout/err to capture in parent process log
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        stream=sys.stderr)
    logger = logging.getLogger(__name__)
    logger.info('path: {}'.format(path))

    stash = Stash(path, pynuxrc, replace)

    # stash images for use with iiif server
    image_report = stash.images()
    info = 'finished stashing images'
    logger.info(info)

    # stash text, audio, video
    file_report = stash.files()
    info = 'finished stashing files'
    logger.info(info)

    # stash thumbnails for text, audio, video
    thumb_report = stash.thumbnails()
    info = 'finished stashing thumbnails'
    logger.info(info)

    # stash media.json files
    mediajson_report = stash.media_json()
    info = 'finished stashing media.json'
    logger.info(info)

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
    print(summary)
    publish_to_harvesting('Deep Harvest for {} done'.format(path),
                          summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='deep harvest a nuxeo folder')
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
