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

    parser = argparse.ArgumentParser(description='get media.json file for given nuxeo path')
    parser.add_argument('path', help="Nuxeo document path")
    parser.add_argument('bucket', help="S3 bucket name")

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()

    nuxeo_path = argv.path
    bucketpath = argv.bucket
    
    print "nuxeo_path:", nuxeo_path

    # get the Nuxeo ID
    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())
    nuxeo_id = nx.get_uid(nuxeo_path)
    print "nuxeo_id:", nuxeo_id

    # see if a media.json file exists on S3 for this object
    conn = connect_s3(calling_format = OrdinaryCallingFormat())    
    bucketpath = bucketpath.strip("/")
    bucketbase = bucketpath.split("/")[0]
    obj_key = "{0}-media.json".format(nuxeo_id)
    s3_url = "s3://{0}/{1}".format(bucketpath, obj_key)
    print "s3_url:", s3_url
    parts = urlparse.urlsplit(s3_url)
    print "bucketpath:", bucketpath
    print "bucketbase:", bucketbase

    try:
        bucket = conn.get_bucket(bucketbase)
    except boto.exception.S3ResponseError:
        print "bucket doesn't exist on S3:", bucketbase

    if not(bucket.get_key(parts.path)):
        print "object doesn't exist on S3:", parts.path
    else:
        print "yup the object exists!:", parts.path
        k = Key(bucket)
        k.key = parts.path
        print "\nfile contents:"
        print k.get_contents_as_string()
        

if __name__ == "__main__":
    sys.exit(main())
