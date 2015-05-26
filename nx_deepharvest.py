#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
import mediajson 
from pynux import utils 
import logging

FORMATS = {"SampleCustomPicture": "image",
           "CustomAudio": "audio",
           "CustomVideo": "video",
           "CustomFile": "file",
          }

def main(argv=None):

    logging.basicConfig(filename='nx_deepharvest.log', level=logging.INFO)
    logging.info('Started')

    parser = argparse.ArgumentParser(description='Create `*-media.json` files for Nuxeo folder.')
    parser.add_argument('path', help="Nuxeo document path")
    parser.add_argument('bucket', help="S3 bucket name")

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()
    
    path = argv.path
    bucket = argv.bucket

    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())

    nxdeepharvest(path, bucket, nx)

    logging.info('Finished')

def nxdeepharvest(path, bucket, nx, s3_conn=None):
    """
    harvest metadata and create a `*-media.json` file
    for objects in collection.
    
    (See https://github.com/ucldc/ucldc-docs/wiki/media.json) 
    """
    mj = mediajson.MediaJson()

    objects = nx.children(path)
    for object in objects:
 
        # get any child info
        structMap = []
        path = object['path']
        children = nx.children(path)
        for child in children:
            child_dict = get_content_div_dict(child)
            structMap.append(child_dict)

        # get the parent info
        parent_dict = get_content_div_dict(object, structMap)

        s3_location = mj.stash_media_json(parent_dict, bucket, s3_conn)

        logging.info('{0} stashed to s3: {1}'.format(path, s3_location))

def get_content_div_dict(object, structMap=None):
    uid, href, label, format = get_object_info(object)
    mj = mediajson.MediaJson()
    content_dict = mj.content_division(uid, href, label, format, children=structMap) 
    
    return content_dict

def get_object_info(object_dict):
    logging.info(object_dict)
    path = object_dict['path']
    uid = object_dict['uid']
    href = get_object_download_url(uid, path)
    label = object_dict['title']
    
    type = object_dict['type']
    try:
        format = FORMATS[type]
        logging.info("determined format {0} based on Nuxeo type {1}".format(format, type))
    except KeyError:
        raise ValueError("Invalid type: {0} for: {1} Expected one of: {2}".format(type, path, FORMATS.keys()))


    return uid, href, label, format 

def get_object_download_url(nuxeo_id, nuxeo_path):
    """ Get object file download URL. We should really put this logic in pynux """
    filename = nuxeo_path.split('/')[-1]
    url = "https://nuxeo-stg.cdlib.org/Nuxeo/nxbigfile/default/{0}/file:content/{1}".format(nuxeo_id, filename)
    return url

if __name__ == "__main__":
    sys.exit(main())
