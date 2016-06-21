#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
import mediajson 
from pynux import utils 
import logging
import urlparse
import urllib
from dplaingestion.mappers.ucldc_nuxeo_mapper import UCLDCNuxeoMapper
from os.path import expanduser

REQUIRED_DOC_PROPS = 'dublincore,ucldc_schema,picture,file,extra_files'

# type Organization should actually be type CustomFile. Adding workaround for now.
TYPE_MAP = {"SampleCustomPicture": "image",
           "CustomAudio": "audio",
           "CustomVideo": "video",
           "CustomFile": "file",
           "Organization": "file"
           }

UCLDC_SCHEMA_MAP = {'ucldc_schema:transcription': 'transcription'}
CHILD_NXQL = "SELECT * FROM Document WHERE ecm:parentId = '{}' AND ecm:currentLifeCycleState != 'deleted' ORDER BY ecm:pos"

class DeepHarvestNuxeo(object):
    ''' 
    deep harvest of nuxeo content for publication in Calisphere
    '''
    def __init__(self, path, s3_bucket_mediajson='static.ucldc.cdlib.org/media_json', **pynux_conf):
        # get configuration and initialize pynux.utils.Nuxeo
        self.nx = None
        if 'pynuxrc' in pynux_conf:
            pynuxrc = pynux_conf['pynuxrc']
            self.nx = utils.Nuxeo(rcfile=open(expanduser(pynuxrc), 'r'))
        elif 'conf_pynux' in pynux_conf:
            conf_pynux = pynux_conf['conf_pynux']
            self.nx = utils.Nuxeo(conf=conf_pynux)
        else:
            self.nx = utils.Nuxeo(conf={}) 

        self.path = urllib.quote(path)
        self.uid = self.nx.get_uid(self.path)
        self.s3_bucket_mediajson = s3_bucket_mediajson
        self.mj = mediajson.MediaJson()

    def fetch_objects(self):
        ''' fetch Nuxeo objects at a given path '''
        objects = []
        query = CHILD_NXQL.format(self.uid)
        for child in self.nx.nxql(query):
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
                    query = CHILD_NXQL.format(current['uid'])
                    for child in self.nx.nxql(query):
                        recurse(child, depth-1)

        recurse(start_obj, depth)

        return harvestable

    def fetch_components(self, start_obj, depth=-1):
        ''' fetch any component objects '''
        components = []

        def recurse(current, depth):
            metadata = self.nx.get_metadata(uid=current['uid'])
            if current != start_obj and self.has_file(metadata):
                components.append(current)
            if depth != 0:
                query = CHILD_NXQL.format(current['uid'])
                for child in self.nx.nxql(query):
                    recurse(child, depth-1)

        recurse(start_obj, depth)

        return components 
 
    def get_parent_metadata(self, obj):
        ''' assemble top-level (parent) object metadata '''
        metadata = {}
        metadata['label'] = obj['title']

        # only provide id, href, format if Nuxeo Document has file attached
        full_metadata = self.nx.get_metadata(uid=obj['uid'])   

        if self.has_file(full_metadata):
            metadata['id'] = obj['uid']
            metadata['href'] = self.get_object_download_url(full_metadata)
            metadata['format'] = self.get_calisphere_object_type(obj['type'])
            if metadata['format'] == 'video':
                metadata['dimensions'] = self.get_video_dimensions(full_metadata)
        
        return metadata 

    def get_component_metadata(self, obj):
        ''' assemble component object metadata ''' 
        metadata = {}
        full_metadata = self.nx.get_metadata(uid=obj['uid'])
        metadata['label'] = obj['title']
        metadata['id'] = obj['uid']
        metadata['href'] = self.get_object_download_url(full_metadata)

        # extract additional  ucldc metadata from 'properties' element
        ucldc_md = self.get_ucldc_schema_properties(full_metadata)

        for key, value in ucldc_md.iteritems():
            metadata[key] = value

        # map 'type'
        metadata['format'] = self.get_calisphere_object_type(obj['type'])

        return metadata

    def has_file(self, metadata):
        ''' given the full metadata for an object, determine whether or not nuxeo document has file content '''
        try:
            file_content = metadata['properties']['file:content']
        except KeyError:
            raise KeyError("Nuxeo object metadata does not contain 'properties/file:content' element. Make sure 'X-NXDocumentProperties' provided in pynux conf includes 'file'")

        if file_content is None:
            return False
        else:
            return True

    def get_ucldc_schema_properties(self, metadata):
        ''' given the full metadata for an object, extract selected values '''
        properties = {} 

        mapper = UCLDCNuxeoMapper(metadata)
        mapper.map_original_record()
        mapper.map_source_resource()

        properties = mapper.mapped_data['sourceResource']
        properties.update(mapper.mapped_data['originalRecord'])

        return properties

    
    def get_object_download_url(self, metadata):
        ''' given the full metadata for an object, get file download url '''
        try:
            file_content = metadata['properties']['file:content']
        except KeyError:
            raise KeyError("Nuxeo object metadata does not contain 'properties/file:content' element. Make sure 'X-NXDocumentProperties' provided in pynux conf includes 'file'")

        if file_content is None:
            return None
        else:
            url = file_content['data']
            return url

    def get_mimetype(self, metadata):
        ''' get the mimetype for a nuxeo content file '''
        try:
            mimetype = metadata['properties']['file:content']['mime-type']
        except TypeError:
            mimetype = None
        except KeyError:
            raise KeyError("Nuxeo object metadata does not contain 'properties/file:content/mime-type' element. Make sure 'X-NXDocumentProperties' provided in pynux conf includes 'file'")
 
        return mimetype

    def get_calisphere_object_type(self, nuxeo_type):
        try:
            calisphere_type = TYPE_MAP[nuxeo_type]
        except KeyError:
            raise ValueError("Invalid type: {0} for: {1} Expected one of: {2}".format(nuxeo_type, self.path, TYPE_MAP.keys()))        
        return calisphere_type 

    def get_video_dimensions(self, metadata):
        ''' given the full metadata for an object, get dimensions in format `width:height` '''
        try:
            vid_info = metadata['properties']['vid:info']
        except KeyError:
            raise KeyError("Nuxeo object metadata does not contain 'properties/vid:info' element. Make sure 'X-NXDocumentProperties' provided in pynux conf includes 'video'")

        try:
            width = vid_info['width']
        except KeyError:
            raise KeyError("Nuxeo object metadata does not contain 'properties/vid:info/width' element.")

        try:
            height = vid_info['height']
        except KeyError:
            raise KeyError("Nuxeo object metadata does not contain 'properties/video:info/height' element.")

        return "{}:{}".format(width, height)

def main(argv=None):
    ''' run deep harvest for Nuxeo collection '''
    parser = argparse.ArgumentParser(description='Deep harvest Nuxeo content at a given path')
    parser.add_argument("path", help="Nuxeo document path")
    parser.add_argument("--bucket", default="static.ucldc.cdlib.org/media_json", help="S3 bucket where media.json files will be stashed")
    parser.add_argument("--pynuxrc", default='~/.pynuxrc', help="rc file for use by pynux")
    if argv is None:
        argv = parser.parse_args()

    dh = DeepHarvestNuxeo(argv.path, argv.bucket, pynuxrc=argv.pynuxrc)
    objects = dh.fetch_objects()
    for obj in objects:
        parent_md = dh.get_parent_metadata(obj) 
        component_md = [dh.get_component_metadata(c) for c in dh.fetch_components(obj)]
        media_json = dh.mj.create_media_json(parent_md, component_md)
        print dh.mj.stash_media_json(obj['uid'], media_json, argv.bucket)


if __name__ == "__main__":
    sys.exit(main())
