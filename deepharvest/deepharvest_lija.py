#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo

class DeepHarvestLija(DeepHarvestNuxeo):
    '''
    deep harvest UCM Lee Institute of Japanese Art nuxeo content for publication in Calisphere
    '''
    def __init__(self, path, s3_bucket_media_json='static.ucldc.cdlib.org/media_json', **pynux_conf):
        super(DeepHarvestLija, self).__init__(path, s3_bucket_media_json, **pynux_conf)        

    def fetch_objects(self):
        ''' 
            fetch Nuxeo objects at a given path. 
            Return QTVR LIJA objects separately 
            (this is a workaround for harvesting until we can fix the structure in Nuxeo
            and have a mechanism for displaying QTVR effectively in the UI)
        '''
        children = self.nx.children(self.path)
        objects = []
        for child in children:
            objects.extend(self.fetch_harvestable(child))

        # determine whether or not this is a QTVR object
        regular_objects = []
        qtvr_objects = []
        for obj in objects:
            if self.is_qtvr_object(obj):
                qtvr_objects.append(obj)
            else:
                regular_objects.append(obj)

        return regular_objects, qtvr_objects

    def is_qtvr_object(self, obj):
        ''' 
            determine if this nuxeo doc is a QTVR object 
            These are objects with 'video/quicktime' and 'image/tiff' components. 
        '''
        parent_md = self.nx.get_metadata(uid=obj['uid']) 
        if self.has_file(parent_md):
            if self.get_mimetype(parent_md) == 'video/quicktime':
                return True 
            else:
                return False
        else:
            components = self.fetch_components(obj)
            types = []
            for c in components:
                component_md = self.nx.get_metadata(uid=c['uid'])
                mimetype = self.get_mimetype(component_md) 
                types.append(mimetype)
            if 'video/quicktime' in types:
                return True
            else:
                return False
 
    def get_qtvr_metadata(self, parent_obj):
        ''' assemble top-level parent object metadata for QTVR objects '''
        parent_metadata = {}
        # parent label is from parent object
        parent_metadata['label'] = parent_obj['title']

        # parent file info is from first child tiff
        components = self.fetch_components(parent_obj)
        for comp in components:
            if comp['type'] == 'Organization':
                continue
            component_md = self.nx.get_metadata(uid=comp['uid'])
            if self.get_mimetype(component_md) == 'image/tiff':
                break
        parent_metadata['href'] = self.get_object_download_url(component_md) 
        parent_metadata['id'] = comp['uid']
        parent_metadata['format'] = 'image'

        # component file info is for the .mov 
        component_metadata = {}
        full_parent_md = self.nx.get_metadata(uid=parent_obj['uid'])
        if self.has_file(full_parent_md):
            if self.get_mimetype(full_parent_md) == 'video/quicktime':
                component_metadata['label'] = parent_obj['title']
                component_metadata['href'] = self.get_object_download_url(full_parent_md)
                component_metadata['id'] = parent_obj['uid']
                component_metadata['format'] = 'file'
            else:
                raise ValueError("Parent file mimetype was not 'video/quicktime' -- something is wrong")
        else:
            for comp in components:
                if comp['type'] == 'Organization':
                    continue
                component_md = self.nx.get_metadata(uid=comp['uid'])
                if self.get_mimetype(component_md) == 'video/quicktime':
                    break
            component_metadata['label'] = parent_obj['title']    
            component_metadata['href'] = self.get_object_download_url(component_md)
            component_metadata['id'] = comp['uid'] 
            component_metadata['format'] = 'file'
 
        return parent_metadata, [component_metadata]

def main(argv=None):
    ''' run deep harvest for Nuxeo collection '''
    parser = argparse.ArgumentParser(description='Deep harvest Nuxeo content at a given path')
    parser.add_argument("path", help="Nuxeo document path")
    parser.add_argument("--bucket", help="S3 bucket where media.json files will be stashed")
    parser.add_argument("--pynuxrc", default='~/.pynuxrc', help="rc file for use by pynux")
    if argv is None:
        argv = parser.parse_args()

    dh = DeepHarvestLija(argv.path, argv.bucket, pynuxrc=argv.pynuxrc)
    regular_objects, qtvr_objects = dh.fetch_objects()

    print "#### regular objects ###"
    for obj in regular_objects:
        parent_md = dh.get_parent_metadata(obj)
        component_md = [dh.get_component_metadata(c) for c in dh.fetch_components(obj)]
        media_json = dh.mj.create_media_json(parent_md, component_md)
        print dh.mj.stash_media_json(obj['uid'], media_json, argv.bucket)

    print "#### qtvr objects ###"
    for obj in qtvr_objects:
        parent_md, component_md = dh.get_qtvr_metadata(obj)
        media_json = dh.mj.create_media_json(parent_md, component_md)
        print dh.mj.stash_media_json(obj['uid'], media_json, argv.bucket)

if __name__ == "__main__":
    sys.exit(main())


"""
Copyright © 2014, Regents of the University of California
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
- Neither the name of the University of California nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
""" 
