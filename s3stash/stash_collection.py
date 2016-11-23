#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import argparse
import logging
import json
import boto
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
import s3stash.s3tools
from s3stash.nxstashref_image import NuxeoStashImage
from s3stash.nxstashref_file import NuxeoStashFile
from s3stash.nxstash_thumb import NuxeoStashThumb
from s3stash.nxstash_mediajson import NuxeoStashMediaJson

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


class Stash(object):
    '''
        stash various files on s3 for a Nuxeo collection
        in preparation for harvesting into Calisphere
    '''

    def __init__(self, path, pynuxrc, replace=False, loglevel=_loglevel_):
        self.logger = logging.getLogger(__name__)

        self.path = path
        self.pynuxrc = pynuxrc
        self.replace = replace

        self.dh = DeepHarvestNuxeo(self.path, '', pynuxrc=self.pynuxrc)

        self.objects = self.dh.fetch_objects()

    def images(self):
        ''' stash Nuxeo image files on s3 '''
        report = {}
        for obj in self.objects:
            nxstash = NuxeoStashImage(obj['path'], IMAGE_BUCKET, IMAGE_REGION,
                                      self.pynuxrc, self.replace)
            report[nxstash.uid] = nxstash.nxstashref()
            for c in self.dh.fetch_components(obj):
                nxstash = NuxeoStashImage(c['path'], IMAGE_BUCKET,
                                          IMAGE_REGION, self.pynuxrc,
                                          self.replace)
                report[nxstash.uid] = nxstash.nxstashref()

        return report

    def files(self):
        ''' stash Nuxeo files of type 'file', 'audio', or 'video' for a
        collection
        '''
        report = {}
        for obj in self.objects:
            nxstash = NuxeoStashFile(obj['path'], FILE_BUCKET, FILE_REGION,
                                     self.pynuxrc, self.replace)
            report[nxstash.uid] = nxstash.nxstashref()
            for c in self.dh.fetch_components(obj):
                nxstash = NuxeoStashFile(c['path'], FILE_BUCKET, FILE_REGION,
                                         self.pynuxrc, self.replace)
                report[nxstash.uid] = nxstash.nxstashref()

        return report

    def thumbnails(self):
        ''' stash thumbnail images for Nuxeo files of type 'file', 'audio',
        or 'video' for a collection
        '''
        report = {}
        for obj in self.objects:
            nxstash = NuxeoStashThumb(obj['path'], THUMB_BUCKET, THUMB_REGION,
                                      self.pynuxrc, self.replace)
            report[nxstash.uid] = nxstash.nxstashref()
            for c in self.dh.fetch_components(obj):
                nxstash = NuxeoStashThumb(c['path'], THUMB_BUCKET,
                                          THUMB_REGION, self.pynuxrc,
                                          self.replace)
                report[nxstash.uid] = nxstash.nxstashref()

        return report

    def media_json(self):
        ''' create and stash media.json files for a nuxeo collection '''
        report = {}
        for obj in self.objects:
            nxstash = NuxeoStashMediaJson(obj['path'], MEDIAJSON_BUCKET,
                                          MEDIAJSON_REGION, self.pynuxrc,
                                          self.replace)
            report[nxstash.uid] = nxstash.nxstashref()

        return report


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


def main(registry_id, pynuxrc="~/.pynuxrc", replace=True, loglevel=_loglevel_):
    # set up logging
    logfile = 'logs/stash_collection_{}'.format(registry_id)
    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    # log to stdout/err to capture in parent process log
    # TODO: save log to S3
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)

    # get nuxeo path
    nxpath = s3stash.s3tools.get_nuxeo_path(registry_id)
    if nxpath is None:
        print "No record found for registry_id: {}".format(registry_id)
        sys.exit()
    info = 'nuxeo_path: {}'.format(nxpath)
    logger.info(info)
    print info, '\n'

    stash = Stash(nxpath, pynuxrc, replace)

    # stash images for use with iiif server
    print 'stashing images...'
    image_report = stash.images()
    info = 'finished stashing images'
    logger.info(info)
    print info
    report_file = "images-{}.json".format(registry_id)
    s3_report(report_file, image_report)
    print "report:\t{}\n".format(report_file)

    # stash text, audio, video
    print 'stashing non-image files (text, audio, video)...'
    file_report = stash.files()
    info = 'finished stashing files'
    logger.info(info)
    print info
    report_file = "files-{}.json".format(registry_id)
    s3_report(report_file, file_report)
    print "report:\t{}\n".format(report_file)

    # stash thumbnails for text, audio, video
    print 'stashing thumbnails for non-image files (text, audio, video)...'
    thumb_report = stash.thumbnails()
    info = 'finished stashing thumbnails'
    logger.info(info)
    print info
    report_file = "thumbs-{}.json".format(registry_id)
    s3_report(report_file, thumb_report)
    print "report:\t{}\n".format(report_file)

    # stash media.json files
    print 'stashing media.json files for collection...'
    mediajson_report = stash.media_json()
    info = 'finished stashing media.json'
    logger.info(info)
    print info
    report_file = "mediajson-{}.json".format(registry_id)
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
    print "SUMMARY:"
    print "objects processed:              {}".format(len(stash.objects))
    print "replaced existing files on s3:  {}".format(stash.replace)
    print "images stashed:                 {}".format(images_stashed)
    print "files stashed:                  {}".format(files_stashed)
    print "thumbnails stashed:             {}".format(thumbs_stashed)
    print "media.json files stashed:       {}".format(mediajson_stashed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Deep harvest a Nuxeo collection')
    parser.add_argument('registry_id', help='UCLDC Registry ID')
    parser.add_argument(
        '--pynuxrc', default='~/.pynuxrc', help='rc file for use by pynux')
    parser.add_argument(
        '--replace',
        action='store_true',
        help='replace files on s3 if they already exist')
    parser.add_argument('--loglevel', default=_loglevel_)

    argv = parser.parse_args()

    registry_id = argv.registry_id
    pynuxrc = argv.pynuxrc
    replace = argv.replace
    loglevel = argv.loglevel

    sys.exit(
        main(
            registry_id, pytnuxrc=pynuxrc, replace=replace, loglevel=loglevel))
