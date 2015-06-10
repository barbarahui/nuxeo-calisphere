#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
from pynux import utils
from boto import connect_s3
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from boto.s3.key import Key
import urlparse

def main(argv=None):

    parser = argparse.ArgumentParser(description='print info for items in collection where media.json file is missing.')
    parser.add_argument('path', help="Nuxeo document path for collection")
    parser.add_argument('bucket', help="S3 bucket name")

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()

    nuxeo_path = argv.path
    bucketpath = argv.bucket
    
    print "collection nuxeo_path:", nuxeo_path

    # get the Nuxeo ID for the collection
    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())
    nuxeo_id = nx.get_uid(nuxeo_path)
    print "collection nuxeo_id:", nuxeo_id

    # connect to S3
    conn = connect_s3(calling_format = OrdinaryCallingFormat())    
    bucketpath = bucketpath.strip("/")
    bucketbase = bucketpath.split("/")[0]
    print "bucketpath:", bucketpath
    print "bucketbase:", bucketbase

    try:
        bucket = conn.get_bucket(bucketbase)
    except boto.exception.S3ResponseError:
        print "bucket doesn't exist on S3:", bucketbase

    items = nx.children(nuxeo_path)
    for item in items:
        obj_key = "{0}-media.json".format(item['uid'])
        s3_url = "s3://{0}/{1}".format(bucketpath, obj_key)
        #print "s3_url:", s3_url
        parts = urlparse.urlsplit(s3_url)
        #print "obj_key", obj_key
        #print "s3_url", s3_url

        if not(bucket.get_key(parts.path)):
            print "object doesn't exist on S3:", parts.path
        '''
        else:
            print "yup the object exists!:", parts.path
        k = Key(bucket)
        k.key = parts.path
        print "\nfile contents:"
        print k.get_contents_as_string()
        '''

if __name__ == "__main__":
    sys.exit(main())
