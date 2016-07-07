#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import argparse
import logging
import json
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
THUMB_REGION = 'us-east-1',
MEDIAJSON_BUCKET = 'static.ucldc.cdlib.org/media_json'
MEDIAJSON_REGION = 'us-east-1'

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
            nxstash = NuxeoStashImage(obj['path'], IMAGE_BUCKET, IMAGE_REGION, self.pynuxrc, self.replace)
            report[nxstash.uid] = nxstash.nxstashref()
            for c in self.dh.fetch_components(obj):
                nxstash = NuxeoStashImage(c['path'], IMAGE_BUCKET, IMAGE_REGION, self.pynuxrc, self.replace)
                report[nxstash.uid] = nxstash.nxstashref()

        return report

    def files(self):
        ''' stash Nuxeo files of type 'file', 'audio', or 'video' for a collection '''
        report = {}
        for obj in self.objects:
            nxstash = NuxeoStashFile(obj['path'], FILE_BUCKET, FILE_REGION, self.pynuxrc, self.replace)
            report[nxstash.uid] = nxstash.nxstashref()
            for c in self.dh.fetch_components(obj):
                nxstash = NuxeoStashFile(c['path'], FILE_BUCKET, FILE_REGION, self.pynuxrc, self.replace)
                report[nxstash.uid] = nxstash.nxstashref()

        return report 

    def thumbnails(self):
        ''' stash thumbnail images for Nuxeo files of type 'file', 'audio', or 'video' for a collection '''
        report = {}
        for obj in self.objects:
            nxstash = NuxeoStashThumb(obj['path'], THUMB_BUCKET, THUMB_REGION, self.pynuxrc, self.replace)
            report[nxstash.uid] = nxstash.nxstashref()
            for c in self.dh.fetch_components(obj):
                nxstash = NuxeoStashThumb(c['path'], THUMB_BUCKET, THUMB_REGION, self.pynuxrc, self.replace)
                report[nxstash.uid] = nxstash.nxstashref()

        return report

    def media_json(self):
        ''' create and stash media.json files for a nuxeo collection '''
        report = {}
        for obj in self.objects:
            nxstash = NuxeoStashMediaJson(obj['path'], MEDIAJSON_BUCKET, MEDIAJSON_REGION, self.pynuxrc, self.replace)
            report[nxstash.uid] = nxstash.nxstashref()

        return report

def main(argv=None):
    parser = argparse.ArgumentParser(description='Deep harvest a Nuxeo collection')
    parser.add_argument('registry_id', help='UCLDC Registry ID')
    parser.add_argument('--pynuxrc', default='~/.pynuxrc', help='rc file for use by pynux')
    parser.add_argument('--replace', action='store_true', help='replace files on s3 if they already exist')
    parser.add_argument('--loglevel', default=_loglevel_)

    if argv is None:
        argv = parser.parse_args()

    registry_id = argv.registry_id
    pynuxrc = argv.pynuxrc
    replace = argv.replace
    loglevel = argv.loglevel

    # set up logging
    logfile = 'logs/stash_collection_{}'.format(registry_id)
    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level, filename=logfile, format='%(asctime)s (%(name)s) [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)
    print "\nlogfile: {}\n".format(logfile)

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
    reportfile = "reports/images-{}.json".format(registry_id)
    with open(reportfile, 'w') as f:
        json.dump(image_report, f, sort_keys=True, indent=4)
    print "report:\t{}\n".format(reportfile)
 
    # stash text, audio, video
    print 'stashing non-image files (text, audio, video)...'
    file_report = stash.files()
    info = 'finished stashing files'
    logger.info(info)
    print info
    reportfile = "reports/files-{}.json".format(registry_id)
    with open(reportfile, 'w') as f:
        json.dump(file_report, f, sort_keys=True, indent=4)
    print "report:\t{}\n".format(reportfile) 

    # stash thumbnails for text, audio, video
    print 'stashing thumbnails for non-image files (text, audio, video)...'
    thumb_report = stash.thumbnails()
    info = 'finished stashing thumbnails'
    logger.info(info)
    print info
    reportfile = "reports/thumbs-{}.json".format(registry_id)
    with open(reportfile, 'w') as f:
        json.dump(thumb_report, f, sort_keys=True, indent=4)
    print "report:\t{}\n".format(reportfile)

    # stash media.json files
    print 'stashing media.json files for collection...'
    mediajson_report = stash.media_json()
    info = 'finished stashing media.json'
    logger.info(info)
    print info
    reportfile = "reports/mediajson-{}.json".format(registry_id)
    with open(reportfile, 'w') as f:
        json.dump(mediajson_report, f, sort_keys=True, indent=4)
    print "report:\t{}\n".format(reportfile)

    # print some information about how it went
    images_stashed = len([key for key, value in image_report.iteritems() if value['stashed']])
    files_stashed = len([key for key, value in file_report.iteritems() if value['stashed']])    
    thumbs_stashed = len([key for key, value in thumb_report.iteritems() if value['stashed']])
    mediajson_stashed = len([key for key, value in mediajson_report.iteritems() if value['stashed']])

    print "SUMMARY:"
    print "objects processed:              {}".format(len(stash.objects))
    print "replaced existing files on s3:  {}".format(stash.replace)
    print "images stashed:                 {}".format(images_stashed)
    print "files stashed:                  {}".format(files_stashed)
    print "thumbnails stashed:             {}".format(thumbs_stashed)
    print "media.json files stashed:       {}".format(mediajson_stashed)

if __name__ == "__main__":
    sys.exit(main())
