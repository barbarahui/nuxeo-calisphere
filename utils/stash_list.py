#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys, os
import argparse
import logging
import s3stash.s3tools
from s3stash.stash_collection import Stash as StashCollection

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

'''
deep harvest a list of objects contained in `filename`
'''
class Stash(StashCollection):

    def __init__(self, path, pynuxrc, filename, replace=False, loglevel=_loglevel_):
        
        self.filename = filename

        super(Stash, self).__init__(path, pynuxrc, replace, loglevel)

        self.logger = logging.getLogger(__name__)


    def fetch_objects(self):

        metadata = [] 

        print "self.filename: {}".format(self.filename)
        with open(self.filename, 'r') as f:
            for line in f:
                path = line.split(' ')[1].strip()
                obj_metadata = self.dh.nx.get_metadata(path=path)
                metadata.append(obj_metadata)

        return metadata

def main(filename, registry_id, pynuxrc="~/.pynuxrc", replace=True, loglevel=_loglevel_):
        # set up logging
    logfile = 'logs/stash_list_{}'.format(registry_id)
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

    # get nuxeo path
    nxpath = s3stash.s3tools.get_nuxeo_path(registry_id)
    if nxpath is None:
        print "No record found for registry_id: {}".format(registry_id)
        sys.exit()
    info = 'nuxeo_path: {}'.format(nxpath)
    logger.info(info)
    print info, '\n'

    stash = Stash(nxpath, pynuxrc, filename, replace)
    filename = os.path.basename('27012_missing')

    # stash images for use with iiif server
    print 'stashing images...'
    image_report = stash.images()
    info = 'finished stashing images'
    logger.info(info)
    print info
    report_file = "images-{}.json".format(filename)
    print "report:\t{}\n".format(report_file)

    # stash text, audio, video
    print 'stashing non-image files (text, audio, video)...'
    file_report = stash.files()
    info = 'finished stashing files'
    logger.info(info)
    print info
    report_file = "files-{}.json".format(filename)
    print "report:\t{}\n".format(report_file)

    # stash thumbnails for text, audio, video
    print 'stashing thumbnails for non-image files (text, audio, video)...'
    thumb_report = stash.thumbnails()
    info = 'finished stashing thumbnails'
    logger.info(info)
    print info
    report_file = "thumbs-{}.json".format(filename)
    print "report:\t{}\n".format(report_file)

    # stash media.json files
    print 'stashing media.json files for collection...'
    mediajson_report = stash.media_json()
    info = 'finished stashing media.json'
    logger.info(info)
    print info
    report_file = "mediajson-{}.json".format(filename)
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
        description='Deep harvest nuxeo objects based on a file listing')
    parser.add_argument('filename', help='name of file containing list of objects')
    parser.add_argument('registry_id', help='UCLDC Registry ID')
    parser.add_argument(
        '--pynuxrc', default='~/.pynuxrc', help='rc file for use by pynux')
    parser.add_argument(
        '--replace',
        action='store_true',
        help='replace files on s3 if they already exist')
    parser.add_argument('--loglevel', default=_loglevel_)

    argv = parser.parse_args()

    filename = argv.filename
    registry_id = argv.registry_id
    pynuxrc = argv.pynuxrc
    replace = argv.replace
    loglevel = argv.loglevel

    sys.exit(
        main(
            filename, registry_id, pynuxrc=pynuxrc, replace=replace, loglevel=loglevel))
