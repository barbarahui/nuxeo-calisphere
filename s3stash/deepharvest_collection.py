#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import argparse
import logging
import json
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
import s3stash

''' stash various files on s3 for a Nuxeo collection in preparation for harvesting into Calisphere '''
class Stash(object):
    ''' stash various files on s3 for a Nuxeo collection in preparation for harvesting into Calisphere '''    
    def __init__(self, registry_id, pynuxrc, replace):
        self.logger = logging.getLogger(__name__)
        
        self.registry_id = registry_id
        self.pynuxrc = pynuxrc
        self.replace = replace

        print registry_id, nxpath


def main(argv=None):
    parser = argparse.ArgumentParser(description='Deep harvest a Nuxeo collection')
    parser.add_argument('registry_id', help='UCLDC Registry ID')
    parser.add_argument('--pynuxrc', default='~/.pynuxrc', help='rc file for use by pynux')
    parser.add_argument('--replace', action='store_true', help='replace files on s3 if they already exist')

    if argv is None:
        argv = parser.parse_args()

    
    # stash text, audio, video
    # stash thumbnails for text, audio, video
    # stash images for use with iiif server
    # stash media.json files

if __name__ == "__main__":
    sys.exit(main())
