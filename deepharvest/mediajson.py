#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import json
import tempfile
from boto import connect_s3
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
import urlparse
import magic
import logging

OBJECT_LEVEL_PROPERTIES = ['format', 'href', 'id', 'label', 'dimensions', 'structMap']
COMPONENT_LEVEL_PROPERTIES = ['format', 'href', 'id', 'label', 'dimensions', 'transcription']
VALID_VALUES = {'format': ['image', 'audio', 'video', 'file']}
S3_URL_FORMAT = "s3://{0}/{1}"
FILENAME_FORMAT = "{0}-media.json"

class MediaJson():
    def __init__(self):
        pass
 
    def create_media_json(self, object, components=[]):
        '''
        Given an object and its components, create a json representation 
        compliant with these specs: https://github.com/ucldc/ucldc-docs/wiki/media.json

        object is a dict of properties
        components is a list of dicts of properties
        '''
        media_json = {}

        # extract parent level metadata
        media_json = self._create_parent_json(object)
        
        # assemble structMap for any components
        structmap = [self._create_component_json(c) for c in components]
        if structmap:
            media_json['structMap'] = structmap

        return media_json 
         
    def _create_parent_json(self, source_object):
        ''' 
           map parent-level metadata for source object to media.json scheme
           source_object is a dict of properties for the item
        '''
        parent_json = {}
        for key, value in source_object.iteritems():
            if key in OBJECT_LEVEL_PROPERTIES:
                if key in VALID_VALUES:
                    if value not in VALID_VALUES[key]:
                        raise ValueError("Invalid {}. Expected one of: {}".format(key, value))
                parent_json[key] = value
       
        return parent_json 

    def _create_component_json(self, source_component):
        '''
            map component-level metadata for source object to media.json scheme
            source_component is a dict of properties for the component
        '''
        component_json = {} 
        for key, value in source_component.iteritems():
            if key in COMPONENT_LEVEL_PROPERTIES:
                if key in VALID_VALUES:
                    if value not in VALID_VALUES[key]:
                        raise ValueError("Invalid {}. Expected one of: {}".format(key, value))    
                component_json[key] = value
      
        return component_json

    def stash_media_json(self, media_dict, bucket, s3_conn=None):
        """ stash <id>-media.json file on S3 """
        id = media_dict['id']
        if not id:
            raise ValueError("id is required")

        tmp_dir = tempfile.mkdtemp()
        filename = FILENAME_FORMAT.format(id)
        tmp_filepath = os.path.join(tmp_dir, filename)
    
        # write json to file 
        self._create_json_file(media_dict, tmp_filepath)

        # stash in s3
        s3_location = self._s3_stash(tmp_filepath, bucket, filename, s3_conn)

        # delete temp stuff
        os.remove(tmp_filepath)
        os.rmdir(tmp_dir)
 
        return s3_location
        
    def _create_json_file(self, content_dict, filepath):
        """ convert dict to json and write to file """
        content_json = json.dumps(content_dict, indent=4, separators=(',', ': '), sort_keys=True)
        with open(filepath, 'wb') as f:
            f.write(content_json)
            f.flush() 

    def _s3_stash(self, filepath, bucketpath, obj_key, conn=None):
       """ Stash a file in the named bucket. 
         `conn` is an optional boto.connect_s3()
       """
       bucketpath = bucketpath.strip("/")
       bucketbase = bucketpath.split("/")[0]   
       s3_url = S3_URL_FORMAT.format(bucketpath, obj_key)
       parts = urlparse.urlsplit(s3_url)
       #mimetype = magic.from_file(filepath, mime=True)
       mimetype = 'application/json'
       
       logging.debug('s3_url: {0}'.format(s3_url))
       logging.debug('bucketpath: {0}'.format(bucketpath))
       logging.debug('bucketbase: {0}'.format(bucketbase))
 
       if conn is None:
           # don't know why calling_format isn't getting read out of .aws/config file
           conn = connect_s3(calling_format = OrdinaryCallingFormat()) 

       try:
           bucket = conn.get_bucket(bucketbase)
       except boto.exception.S3ResponseError:
           bucket = conn.create_bucket(bucketbase)

       if not(bucket.get_key(parts.path)):
           key = bucket.new_key(parts.path)
           key.set_metadata("Content-Type", mimetype)
           key.set_contents_from_filename(filepath)
           logging.info("created {0}".format(s3_url))
       else:
           logging.info("key already existed; updating: {0}".format(s3_url))
           key = bucket.get_key(parts.path)
           key.set_metadata("Content-Type", mimetype)
           key.set_contents_from_filename(filepath) 

       return s3_url 

if __name__ == '__main__':
    sys.exit(main())
