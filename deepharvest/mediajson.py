#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys, os
import json
import tempfile
from boto import connect_s3
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
import urlparse
import logging

OBJECT_LEVEL_PROPERTIES = ['format', 'href', 'id', 'label', 'dimensions', 'structMap']
VALID_VALUES = {'format': ['image', 'audio', 'video', 'file', '3d']}

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
            if value:
                if key in VALID_VALUES:
                    if value not in VALID_VALUES[key]:
                        raise ValueError("Invalid {}. Expected one of: {}".format(key, value))    
                component_json[key] = value
      
        return component_json

if __name__ == '__main__':
    sys.exit(main())
