#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import json
import tempfile
import boto
import urlparse
import magic

class MediaJson:
    
    def __init__(self):
        self.file_formats = ['image', 'audio', 'video', 'file']        
        self.filename_format = "{0}-media.json"

    def content_division(self, id, href, label, format='image', children={}):
         
        if format not in self.file_formats:
            raise ValueError("Invalid format type. Expected one of: %s" % self.file_formats)

        content_division = {}
        content_division['id'] = id
        content_division['href'] = href
        content_division['label'] = label
        content_division['format'] = format

        if children:
            # check that this is a valid content division?
            content_division['structMap'] = children

        return content_division

    def stash_media_json(self, media_dict, bucket, s3_conn=None):
        """ stash <id>-media.json file on S3 """
        # perform any sort of check that this valid structure? yes, use jsonschema package
        id = media_dict['id']
        if not id:
            raise ValueError("id is required")

        tmp_dir = tempfile.mkdtemp()
        filename = self.filename_format.format(id)
        tmp_filepath = os.path.join(tmp_dir, filename)
    
        # write json to file 
        self.create_json_file(media_dict, tmp_filepath)

        # stash in s3
        s3_location = self.s3_stash(tmp_filepath, bucket, filename, s3_conn)

        # delete temp stuff
        os.remove(tmp_filepath)
        os.rmdir(tmp_dir)
 
        return s3_location
        
    def create_json_file(self, content_dict, filepath):
        """ convert dict to json and write to file """
        content_json = json.dumps(content_dict)
        with open(filepath, 'wb') as f:
            f.write(content_json)
            f.flush() 

    def s3_stash(self, filepath, bucketpath, obj_key, conn=None):
       """ Stash a file in the named bucket. 
         `conn` is an optional boto.connect_s3()
       """
       bucketpath = bucketpath.strip("/")
       bucketbase = bucketpath.split("/")[0]   
       s3_url = "s3://{0}/{1}".format(bucketpath, obj_key)
       parts = urlparse.urlsplit(s3_url)
       mimetype = magic.from_file(filepath, mime=True)
       
       if conn is None:
           conn = boto.connect_s3()

       try:
           bucket = conn.get_bucket(bucketbase)
       except boto.exception.S3ResponseError:
           bucket = conn.create_bucket(bucketbase)

       if not(bucket.get_key(parts.path)):
           key = bucket.new_key(parts.path)
           key.set_metadata("Content-Type", mimetype)
           key.set_contents_from_filename(filepath)
           print "created", s3_url
       else:
           print "key already existed:", s3_url

       return s3_url 
