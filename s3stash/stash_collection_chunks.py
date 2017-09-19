#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, sys
import fnmatch
import argparse 
import logging
import json
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
import s3stash.s3tools
from s3stash.nxstashref_image import NuxeoStashImage
from s3stash.nxstashref_file import NuxeoStashFile
from s3stash.nxstash_thumb import NuxeoStashThumb
from s3stash.nxstash_mediajson import NuxeoStashMediaJson
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

class Stash(object):
    '''
        stash various files on s3 for a Nuxeo collection
        in preparation for harvesting into Calisphere

    '''

    def __init__(self, pynuxrc, replace=False):
        self.logger = logging.getLogger(__name__)

        self.pynuxrc = pynuxrc
        self.replace = replace


    def deepharvest(self, metadata):
        ''' given a set of nuxeo metadata for a doc, deep harvest it '''

        self.logger.info("Processing {}".format(metadata['uid']))
     
        dh = DeepHarvestNuxeo('')
        type = dh.get_calisphere_object_type(metadata['type'])
        self.logger.info("Type: {}".format(type))


        report = {}
        if type == 'image':
            ''' stash image '''
            nxstash = NuxeoStashImage(metadata['path'], IMAGE_BUCKET, IMAGE_REGION,
                                      self.pynuxrc, self.replace, metadata=metadata)
            report[nxstash.uid] = nxstash.nxstashref()
        
        print report
 
        # if type in ['file', 'audio', 'video']:
            # stash file
            # stash thumbnail

        # stash media.json
        '''
        # we only want to do this for parent objects!
        report = {}
        nxstash = NuxeoStashMediaJson(metadata['path'], MEDIAJSON_BUCKET,
                                          MEDIAJSON_REGION, self.pynuxrc,
                                          self.replace)
        report[nxstash.uid] = nxstash.nxstashref()

        print report 
        
        '''

def main(registry_id, pynuxrc="~/.pynuxrc", replace=True, loglevel=_loglevel_):
    # set up logging
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

    stash = Stash(pynuxrc, replace)
    chunkdir = 'chunks'

    pattern = '{}_*.txt'.format(registry_id)

    chunks = {}
    indices = []

    for file in os.listdir(chunkdir):
        if fnmatch.fnmatch(file, pattern):

            index = file.split('.txt')[0] 
            index = index.split('_')[1]
            index = int(index)

            #with open(os.path.join(chunkdir, file), 'r') as f:
            #    md = json.load(f)

            indices.append(index)
            chunks[index] = file 

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(chunks)
    #pp.pprint(indices)

    for index in sorted(indices):
        file = chunks[index]
        filepath = os.path.join(chunkdir, file)
        logger.info("Working on file: {}".format(filepath))
        with open(filepath, 'r') as f:
            data = json.load(f)

        for md in data:
            stash.deepharvest(md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Deep harvest a Nuxeo collection in chunks')
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
            registry_id, pynuxrc=pynuxrc, replace=replace, loglevel=loglevel))
