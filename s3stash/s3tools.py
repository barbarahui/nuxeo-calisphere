#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto
import logging
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
import urlparse

S3_URL_FORMAT = "s3://{0}/{1}"

def s3stash(filepath, bucket, key, region, mimetype, replace=False):
       """ 
       Stash file in S3 bucket.
       """
       logger = logging.getLogger(__name__)

       logger.info("filepath: {}".format(filepath))
       logger.info("bucket: {}".format(bucket))
       logger.info("key: {}".format(key))
       logger.info("region: {}".format(region))
       logger.info("mimetype: {}".format(mimetype))

       report = {}
       bucketpath = bucket.strip("/")
       bucketbase = bucket.split("/")[0]
       s3_url = S3_URL_FORMAT.format(bucketpath, key)
       parts = urlparse.urlsplit(s3_url)

       logger.info("bucketpath: {}".format(bucketpath))
       logger.info("bucketbase: {}".format(bucketbase))
       logger.info("s3_url: {}".format(s3_url))

       # FIXME ugh this is such a hack. not sure what is going on here.
       if region == 'us-east-1':
           conn = boto.connect_s3(calling_format = OrdinaryCallingFormat())
       else:
           conn = boto.s3.connect_to_region(region)

       try:
           bucket = conn.get_bucket(bucketbase)
       except boto.exception.S3ResponseError:
           bucket = conn.create_bucket(bucketbase, location=region)
           logger.info("Created S3 bucket {}".format(bucketbase))

       if not(bucket.get_key(parts.path)):
           key = bucket.new_key(parts.path)
           key.set_metadata("Content-Type", mimetype)
           key.set_contents_from_filename(filepath)
           msg = "created {0}".format(s3_url)
           action = 'created'
           logger.info(msg)
       elif replace:
           key = bucket.get_key(parts.path)
           key.set_metadata("Content-Type", mimetype)
           key.set_contents_from_filename(filepath)
           msg = "re-uploaded {}".format(s3_url)
           action = 'replaced'
           logger.info(msg)
       else:
           msg = "key already existed; not re-uploading {0}".format(s3_url)
           action = 'skipped'
           logger.info(msg)

       report['s3_url'] = s3_url
       report['msg'] = msg
       report['action'] = action
       report['stashed'] = True

       return True, report

def is_s3_stashed(bucket, key, region):
       """ Check for existence of key on S3.
       """
       logger = logging.getLogger(__name__)
       key_exists = False

       bucketpath = bucket.strip("/")
       bucketbase = bucket.split("/")[0]
       s3_url = S3_URL_FORMAT.format(bucketpath, key)
       parts = urlparse.urlsplit(s3_url)

       # FIXME ugh this is such a hack. not sure what is going on here.
       if region == 'us-east-1':
           conn = boto.connect_s3(calling_format = OrdinaryCallingFormat())
       else:
           conn = boto.s3.connect_to_region(region)

       try:
           bucket = conn.get_bucket(bucketbase)
       except boto.exception.S3ResponseError:
           logger.info("Bucket does not exist: {}".format(bucketbase))
           return False

       if bucket.get_key(parts.path):
           return True
       else:
           return False
