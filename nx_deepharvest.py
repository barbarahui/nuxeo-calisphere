#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
import mediajson 
from pynux import utils 
import pprint

pp = pprint.PrettyPrinter()

def main(argv=None):

    parser = argparse.ArgumentParser(description='Create `*-media.json` files for Nuxeo folder.')
    parser.add_argument('path', help="Nuxeo document path")
    parser.add_argument('bucket', help="S3 bucket name")

    if argv is None:
        argv = parser.parse_args()
    
    path = argv.path
    bucket = argv.bucket

    nxdeepharvest(path, bucket)

def nxdeepharvest(path, bucket, s3_conn=None):
    """
    harvest metadata and create a `*-media.json` file
    for objects in collection.
    
    (See https://github.com/ucldc/ucldc-docs/wiki/media.json) 
    """
    mj = mediajson.MediaJson()
    nx = utils.Nuxeo()

    objects = nx.children(path)
    for object in objects:
        # get the kids' info for the structMap element

        # get the parent info 
        path = object['path']
        uid = object['uid']
        href = get_object_download_url(uid, path)
        label = object['title']
        media_dict = mj.content_division(uid, href, label)
 
        print mj.stash_media_json(media_dict, bucket)

def get_object_download_url(nuxeo_id, nuxeo_path):
    """ Get object file download URL. We should really put this logic in pynux """
    filename = nuxeo_path.split('/')[-1]
    url = "https://nuxeo-stg.cdlib.org/Nuxeo/nxbigfile/default/{0}/file:content/{1}".format(nuxeo_id, filename)
    return url

if __name__ == "__main__":
    sys.exit(main())
