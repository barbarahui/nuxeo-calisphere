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
        self.test_component_with_transcript = os.path.join(test_json_dir, 'component_object_with_transcript.json')
        self.test_nuxeo_full_md_transcript = os.path.join(test_json_dir, 'nuxeo_full_metadata_transcript.json')
        self.test_nuxeo_full_metadata = os.path.join(test_json_dir, 'nuxeo_full_metadata.json')
        self.test_nuxeo_organizational_object = os.path.join(test_json_dir, 'nuxeo_organizational_object.json')
        self.test_nuxeo_empty_folder_object = os.path.join(test_json_dir, 'nuxeo_empty_folder_object.json')

    def test_init(self):
        ''' test initialization of DeepHarvestNuxeo object '''
        dh = deepharvest_nuxeo.DeepHarvestNuxeo(self.path, self.s3_mediajson, self.pynuxrc)
        self.assertEqual(dh.path, self.path)
        self.assertEqual(dh.s3_bucket_mediajson, self.s3_mediajson)

    def test_fetch_objects(self):
        ''' test fetching of Nuxeo objects at a given path ''' 
        objects = self.dh.fetch_objects() # FIXME mock this generator so we don't actually go over the network
        self.assertEqual(sum(1 for ob in objects), 215) # FIXME bad test! # of objects might change...
   
    def test_fetch_objects_nested(self):
        ''' test fetching of Nuxeo objects for a collection that has nested folders '''
        dh = deepharvest_nuxeo.DeepHarvestNuxeo('/asset-library/UCR/SabinoOsuna', self.s3_mediajson, self.pynuxrc)
        objects = dh.fetch_objects()
        self.assertEqual(sum(1 for ob in objects), 427) # FIXME bad test! # of objects might change...

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

    def test_get_ucldc_schema_properties(self):
        ''' test getting ucldc_schema metadata for object '''
        obj = json.load(open(self.test_nuxeo_full_md_transcript))
        ucldc_md = self.dh.get_ucldc_schema_properties(obj)
        self.assertEqual(ucldc_md['transcription'], obj['properties']['ucldc_schema:transcription'])

    def test_get_component_metadata_with_transcript(self):
        ''' test getting metadata for a component that has a transcription '''
        obj = json.load(open(self.test_component_with_transcript))
        metadata = self.dh.get_component_metadata(obj)
        self.assertEqual(metadata['transcription'], u'[written above date]:Stanton Hospital, Washington. City D.C.\n\nThe old year has gone, gone forever with all its joys, sorrows, and cares, a New Year is just began, our hearts beat high with thankfulness and of hope for the future, and we begin the New Year with a merry greeting to all, especially to our absent comrads in the field, may the God of Battles protect all of them and ere another New Years day resore them again to our waiting anxious friends. - a greeting to our bereaved ones with tender sympathy. Those who mourn the loss of these gone forth-to-battle never to return, - to our country in I all levels of Freedom a greeting  with the wish that soon the Angel of Peace will find its wings and rush over our beloved country. This had been a cold but beautiful day in the morning was very busy on office work. recieved a letter from [illegible], answered the same, in the evening. also wrote short letter to my cousin with the mount pleasant hospital, in the afternoon was visited by my friend Mr. Mom and two members of my Regt. was not out of the hospital today. sent this morning Chronicle to Aunt Mercy.')

    def test_fetch_harvestable_not_nested(self):
        ''' test that a non-nested object is identified as harvestable '''
        non_nested_obj = json.load(open(self.test_simple_object))
        harvestable = self.dh.fetch_harvestable(non_nested_obj) 
        self.assertEqual(harvestable, [non_nested_obj])

    def test_fetch_harvestable_nested(self):
        ''' test that nested objects are identified as harvestable '''
        # FIXME bad test
        organizational_obj = json.load(open(self.test_nuxeo_organizational_object))
        harvestable = self.dh.fetch_harvestable(organizational_obj)
        self.assertEqual(len(harvestable), 50)

    def test_fetch_harvestable_empty_folder(self):
        ''' test that an empty folder doesn't return any harvestable objects '''
        # FIXME another bad test
        empty_folder_obj = json.load(open(self.test_nuxeo_empty_folder_object))
        harvestable = self.dh.fetch_harvestable(empty_folder_obj)
        self.assertEqual(len(harvestable), 0)

if __name__ == '__main__':
    main()
