#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys, os
import json
import boto3 
import mimetypes

TOP_LEVEL_PROPERTIES = ['format', 'href', 'id', 'label', 'dimensions', 'structMap', 'mimetype', 'orig_filename', 'version', 'metadata']

def main():

    ''' iterate over the media.json files in given s3 bucket 
        probably want to create a separate process for getting a list of media.json files
        that are current and that we want to process.
        there is likely a lot of crud on s3
    '''
    bucketname = "static.ucldc.cdlib.org"
    # keyname = "media_json_2/a0df3f41-8c54-42dd-b7f3-f3bf95011c9f-media.json" # nightingale tiff
    keyname = "media_json_2/08999aaf-03f9-4054-943e-24f66b2ac9fe-media.json" # Henry O. Nightingale diary, 1865
    #keyname = "media_json_2/0061295f-e68f-48bc-8c81-8fb596cd0bd9-media.json" # Woman taking patient's weight at SFGH AIDS Clinic
    s3 = boto3.client('s3')

    # download media.json file
    with open("tmp.json", "wb") as f:
        s3.download_fileobj(bucketname, keyname, f)

    # read file into a dict
    with open("tmp.json", "r") as f:
        json_version_1 = json.load(f)
    
    # do parent object
    version2 = transform_top_level(json_version_1)

    # do structMap (for complex objects) 
    if json_version_1.get('structMap'):
        version2['structMap'] = transform_structmap(json_version_1['structMap'])

    # stash new version on s3
    version2_filename = "version2.json"
    with open(version2_filename, "wb") as f:
        json.dump(version2, f, sort_keys=True, indent=4)    

    s3.upload_file(version2_filename, bucketname, keyname)

def transform_top_level(content):
    ''' add new properties to enable file download from calisphere '''
    # new top level properties: mimetype, orig_filename, version
    href = content['href']
    content['orig_filename'] = get_orig_filename(href)
    content['mimetype'] = get_mimetype(href)
    content['version'] = '2.0'

    return content
    
def transform_structmap(structMap):
    ''' transform according to new spec: nest metadata to avoid namespace clash
        https://github.com/ucldc/ucldc-docs/wiki/media.json
    '''
    new_structMap = []
    for child in structMap:
        new_child = {}
        metadata = {}
        for key, value in child.iteritems():
            if key == 'metadata':
                metadata = value
            elif key in TOP_LEVEL_PROPERTIES:
                print(key)
                new_child[key] = value
            else:
                print(key)
                metadata[key] = value
        new_child['metadata'] = metadata
        href = child['href']
        new_child['mimetype'] = get_mimetype(href)
        new_child['orig_filename'] = get_orig_filename(href)
         
        new_structMap.append(new_child)

    return new_structMap 

def get_mimetype(path):
    # mimetype
    mimetype = mimetypes.guess_type(path)[0]
    return mimetype

def get_orig_filename(path):
    # orig filename
    filename = os.path.basename(path) 
    return filename

    # add version number to media.json file

if __name__ == "__main__":
    sys.exit(main())
