#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
import mediajson 
from pynux import utils 
import logging
import urlparse

# type Organization should actually be type CustomFile. Adding workaround for now.
TYPE_MAP = {"SampleCustomPicture": "image",
           "CustomAudio": "audio",
           "CustomVideo": "video",
           "CustomFile": "file",
           "Organization": "file"
           }

class DeepHarvestNuxeo():
    ''' 
    deep harvest of nuxeo content for publication in Calisphere
    '''
    def __init__(self, path, s3_bucket_mediajson, s3_bucket_ref_img):
        self.path = path
        self.s3_bucket_mediajson = s3_bucket_mediajson
        self.s3_bucket_ref_img = s3_bucket_ref_img 
        # set up logging
        self.mj = mediajson.MediaJson()
        self.nx = utils.Nuxeo(rcfile='~/.pynuxrc-prod') # FIXME

    def fetch_objects(self):
        ''' fetch Nuxeo objects at a given path '''
        objects = self.nx.children(self.path)
        return objects
        
    def fetch_components(self, start_obj, depth=-1):
        ''' fetch any component objects '''
        components = []

        def recurse(current, depth):
            if current != start_obj:
                components.append(current)
            if depth != 0:
                for child in self.nx.children(current['path']):
                    recurse(child, depth-1)

        recurse(start_obj, depth)

        return components 
 
    def get_parent_metadata(self, obj):
        ''' assemble top-level (parent) object metadata '''
        metadata = {}
        metadata['label'] = obj['title']
        metadata['id'] = obj['uid']
        metadata['href'] = self.get_object_download_url(obj['uid'], obj['path'])
        metadata['format'] = self.get_calisphere_object_type(obj['type'])

        return metadata 

    def get_component_metadata(self, obj):
        ''' assemble component object metadata ''' 
        metadata = {}
        metadata['label'] = obj['title']
        metadata['id'] = obj['uid']
        metadata['href'] = self.get_object_download_url(obj['uid'], obj['path'])
        metadata['format'] = self.get_calisphere_object_type(obj['type'])

        return metadata

    def get_object_download_url(self, nuxeo_id, nuxeo_path):
        """ Get object file download URL. We should really put this logic in pynux """
        parts = urlparse.urlsplit(self.nx.conf["api"])
        path_base = parts.path.split('/')[0]
        filename = nuxeo_path.split('/')[-1]
        url = u'{0}://{1}/nuxeo/nxbigfile/default/{2}/file:content/{3}'.format(parts.scheme, parts.netloc, nuxeo_id, filename)

        return url

    def get_calisphere_object_type(self, nuxeo_type):
        try:
            calisphere_type = TYPE_MAP[nuxeo_type]
        except KeyError:
            raise ValueError("Invalid type: {0} for: {1} Expected one of: {2}".format(nuxeo_type, self.path, TYPE_MAP.keys()))        
        return calisphere_type 

    def assemble_object_metadata(self, parent, components=None):
        ''' 
        given parent and component metadata, assemble one dict for the
        object to pass to mediajson, including structMap
        '''
        assembled = parent
        if components:
            assembled['structMap'] = components
 
        return assembled        

if __name__ == "__main__":
    sys.exit(main())
