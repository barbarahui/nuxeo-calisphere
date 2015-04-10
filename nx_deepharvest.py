#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
import mediajson 
from pynux import utils 

def main(argv=None):

    # FIXME add logging?
    # FIXME add tests
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
 
        # get any child info
        structMap = []
        children = nx.children(object['path'])
        for child in children:
            child_dict = get_content_div_dict(child)
            structMap.append(child_dict)

        # get the parent info
        parent_dict = get_content_div_dict(object, structMap)

        print mj.stash_media_json(parent_dict, bucket, s3_conn)

def get_content_div_dict(object, structMap=None):
    uid, href, label = get_object_info(object)
    mj = mediajson.MediaJson()
    content_dict = mj.content_division(uid, href, label, children=structMap) 
    
    return content_dict

def get_object_info(object_dict):
    path = object_dict['path']
    uid = object_dict['uid']
    href = get_object_download_url(uid, path)
    label = object_dict['title']

    return uid, href, label

def get_object_download_url(nuxeo_id, nuxeo_path):
    """ Get object file download URL. We should really put this logic in pynux """
    filename = nuxeo_path.split('/')[-1]
    url = "https://nuxeo-stg.cdlib.org/Nuxeo/nxbigfile/default/{0}/file:content/{1}".format(nuxeo_id, filename)
    return url

if __name__ == "__main__":
    sys.exit(main())
