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

UCLDC_SCHEMA_MAP = {'ucldc_schema:transcription': 'transcription'}

class DeepHarvestNuxeo():
    ''' 
    deep harvest of nuxeo content for publication in Calisphere
    '''
    def __init__(self, path, s3_bucket_mediajson, pynuxrc):
        self.path = path
        self.s3_bucket_mediajson = s3_bucket_mediajson
        self.pynuxrc = pynuxrc
        # set up logging
        self.mj = mediajson.MediaJson()
        self.nx = utils.Nuxeo(rcfile=self.pynuxrc) # FIXME

    def fetch_objects(self):
        ''' fetch Nuxeo objects at a given path '''
        children = self.nx.children(self.path)
        objects = []
        for child in children:
            objects.extend(self.fetch_harvestable(child))

        return objects
        
    def fetch_harvestable(self, start_obj, depth=-1):
        ''' 
            if the given Nuxeo object is harvestable, return it.
            if it's an organizational folder, search recursively inside it for all harvestable objects 
            (not components -- just top-level objects)
        '''
        harvestable = []

        def recurse(current, depth):
            if current['type'] != 'Organization':
                harvestable.append(current)
            if depth != 0:
                if current['type'] == 'Organization':
                    for child in self.nx.children(current['path']):
                        recurse(child, depth-1)

        recurse(start_obj, depth)

        return harvestable

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

        ucldc_md = self.get_ucldc_schema_properties(self.nx.get_metadata(uid=obj['uid']))
        for key, value in ucldc_md.iteritems():
            metadata[key] = value

        metadata['href'] = self.get_object_download_url(obj['uid'], obj['path'])
        metadata['format'] = self.get_calisphere_object_type(obj['type'])
        
        return metadata

    def get_ucldc_schema_properties(self, metadata):
        ''' given the full metadata for an object, extract selected values '''
        properties = {} 
        for key, value in UCLDC_SCHEMA_MAP.iteritems():
            properties[value] = metadata['properties'][key]
 
        return properties

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

def main(argv=None):
    ''' run deep harvest for Nuxeo collection '''
    parser = argparse.ArgumentParser(description='Deep harvest Nuxeo content at a given path')
    parser.add_argument("path", help="Nuxeo document path")
    parser.add_argument("bucket", help="S3 bucket where media.json files will be stashed")
    parser.add_argument("--pynuxrc", default='~/.pynuxrc-prod', help="rc file for use by pynux")
    if argv is None:
        argv = parser.parse_args()

    dh = DeepHarvestNuxeo(argv.path, argv.bucket, argv.pynuxrc)
    objects = dh.fetch_objects()
    for obj in objects:
        parent_md = dh.get_parent_metadata(obj) 
        component_md = [dh.get_component_metadata(c) for c in dh.fetch_components(obj)]
        media_json = dh.mj.create_media_json(parent_md, component_md)
        print dh.mj.stash_media_json(media_json, argv.bucket)

if __name__ == "__main__":
    sys.exit(main())
