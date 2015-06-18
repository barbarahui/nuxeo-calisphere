#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import unittest
from deepharvest import deepharvest_nuxeo
import ast
import json

class DeepHarvestNuxeoSimpleTestCase(unittest.TestCase):

    def setUp(self):

        self.path = "asset-library/UCD/Halberstadt"
        self.s3_mediajson = "static.ucldc.cdlib.org/media_json"
        self.s3_refimages = "ucldc-nuxeo-ref-images"
        self.pynuxrc = "~/.pynuxrc-prod"
        self.dh = deepharvest_nuxeo.DeepHarvestNuxeo(self.path, self.s3_mediajson, self.pynuxrc)

        test_json_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'json')
        self.test_simple_object = os.path.join(test_json_dir, 'simple_object.json')
        self.test_complex_object_depth_one = os.path.join(test_json_dir, 'complex_object_one_deep.json')
        self.test_complex_object_depth_two = os.path.join(test_json_dir, 'complex_object_two_deep.json')
        self.test_component_object = os.path.join(test_json_dir, 'component_object.json')
 
    def test_init(self):
        ''' test initialization of DeepHarvestNuxeo object '''
        dh = deepharvest_nuxeo.DeepHarvestNuxeo(self.path, self.s3_mediajson, self.pynuxrc)
        self.assertEqual(dh.path, self.path)
        self.assertEqual(dh.s3_bucket_mediajson, self.s3_mediajson)

    def test_fetch_objects(self):
        ''' test fetching of Nuxeo objects at a given path ''' 
        objects = self.dh.fetch_objects() # FIXME mock this generator so we don't actually go over the network
        self.assertEqual(sum(1 for ob in objects), 215) # FIXME bad test! # of objects might change...
   
    def test_fetch_components_none(self):
        ''' test getting components for simple object. should be none. '''
        obj = json.load(open(self.test_simple_object))
        components = self.dh.fetch_components(obj) # mock
        self.assertEqual(len(components), 0) # FIXME 

    def test_fetch_components_depth_one(self):
        ''' test getting components for object with nested depth == 1 '''
        obj = json.load(open(self.test_complex_object_depth_one))
        components = self.dh.fetch_components(obj) # mock so we don't actually go over network
        self.assertEqual(len(components), 2) # FIXME bad test!

    def test_fetch_components_depth_several(self):
        ''' test getting components for object with nested depth > 1 '''
        # FIXME this takes too long to run
        #obj = json.load(open(self.test_complex_object_depth_two))
        #components = self.dh.fetch_components(obj) # mock so we don't actually go over network
        #self.assertEqual(len(components), 61) # FIXME bad test! 

    def test_get_parent_metadata(self):
        ''' test getting top-level (parent) metadata for nuxeo object '''
        obj = json.load(open(self.test_simple_object))
        metadata = self.dh.get_parent_metadata(obj)
        self.assertEqual(metadata['label'], u'Wooden box filled with vegetables, fruits, french fries, pie and shrimp')
        self.assertEqual(metadata['id'], u'fb0198b6-ffe6-483a-bb04-ef6f6c3504af')
        self.assertEqual(metadata['href'], u'https://nuxeo.cdlib.org/nuxeo/nxbigfile/default/fb0198b6-ffe6-483a-bb04-ef6f6c3504af/file:content/AlarmtillRGB.tif')
        self.assertEqual(metadata['format'], 'image')

    def test_get_component_metadata(self):
        ''' test getting metadata for a component of a complex object '''
        component_obj = json.load(open(self.test_component_object))
        metadata = self.dh.get_component_metadata(component_obj) 
        self.assertEqual(metadata['label'], u'UCM_LI_2003_063B_K.tif')
        self.assertEqual(metadata['id'], u'510d8b6e-8ad3-48c9-a1f7-5e522ffa9fe9')
        self.assertEqual(metadata['href'], u'https://nuxeo.cdlib.org/nuxeo/nxbigfile/default/510d8b6e-8ad3-48c9-a1f7-5e522ffa9fe9/file:content/UCM_LI_2003_063B_K.tif')
        self.assertEqual(metadata['format'], 'image')

    # test video

    # test audio

    # test complex multi-type

if __name__ == '__main__':
    main()
