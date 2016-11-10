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
        self.pynuxrc = "~/.pynuxrc"
        self.dh = deepharvest_nuxeo.DeepHarvestNuxeo(self.path, self.s3_mediajson, pynuxrc=self.pynuxrc)

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
        self.test_nuxeo_object_no_file = os.path.join(test_json_dir, 'nuxeo_object_no_file.json')

    def test_init(self):
        ''' test initialization of DeepHarvestNuxeo object '''
        dh = deepharvest_nuxeo.DeepHarvestNuxeo(self.path, self.s3_mediajson, pynuxrc=self.pynuxrc)
        self.assertEqual(dh.path, self.path)
        self.assertEqual(dh.s3_bucket_mediajson, self.s3_mediajson)

    def test_fetch_objects(self):
        ''' test fetching of Nuxeo objects at a given path ''' 
        objects = self.dh.fetch_objects() # FIXME mock this generator so we don't actually go over the network
        self.assertEqual(sum(1 for ob in objects), 215) # FIXME bad test! # of objects might change...
   
    def test_fetch_objects_nested(self):
        ''' test fetching of Nuxeo objects for a collection that has nested folders '''
        #dh = deepharvest_nuxeo.DeepHarvestNuxeo('/asset-library/UCR/SabinoOsuna', self.s3_mediajson, pynuxrc=self.pynuxrc)
        #objects = dh.fetch_objects()
        #self.assertEqual(sum(1 for ob in objects), 427) # FIXME bad test! # of objects might change...

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

    def test_get_metadata_no_file(self):
        ''' test that getting the metadata for an object with no file results in empty id and format '''
        # TODO rewrite this test to not go against live data
        '''
        obj = json.load(open(self.test_nuxeo_object_no_file))
        metadata = self.dh.get_parent_metadata(obj)
        self.assertNotIn('id', metadata)
        self.assertNotIn('format', metadata)
        '''

    def test_get_component_metadata_with_transcript(self):
        ''' test getting metadata for a component that has a transcription '''
        #obj = json.load(open(self.test_component_with_transcript))
        #metadata = self.dh.get_component_metadata(obj)
        #self.assertEqual(metadata['transcription'], u'[written above date]:Stanton Hospital, Washington. City D.C.\n\nThe old year has gone, gone forever with all its joys, sorrows, and cares, a New Year is just began, our hearts beat high with thankfulness and of hope for the future, and we begin the New Year with a merry greeting to all, especially to our absent comrads in the field, may the God of Battles protect all of them and ere another New Years day resore them again to our waiting anxious friends. - a greeting to our bereaved ones with tender sympathy. Those who mourn the loss of these gone forth-to-battle never to return, - to our country in I all levels of Freedom a greeting  with the wish that soon the Angel of Peace will find its wings and rush over our beloved country. This had been a cold but beautiful day in the morning was very busy on office work. recieved a letter from [illegible], answered the same, in the evening. also wrote short letter to my cousin with the mount pleasant hospital, in the afternoon was visited by my friend Mr. Mom and two members of my Regt. was not out of the hospital today. sent this morning Chronicle to Aunt Mercy.')

    def test_fetch_harvestable_not_nested(self):
        ''' test that a non-nested object is identified as harvestable '''
        non_nested_obj = json.load(open(self.test_simple_object))
        harvestable = self.dh.fetch_harvestable(non_nested_obj) 
        self.assertEqual(harvestable, [non_nested_obj])

    def test_fetch_harvestable_nested(self):
        ''' test that nested objects are identified as harvestable '''
        # FIXME bad test
        #organizational_obj = json.load(open(self.test_nuxeo_organizational_object))
        #harvestable = self.dh.fetch_harvestable(organizational_obj)
        #self.assertEqual(len(harvestable), 50)

    def test_fetch_harvestable_empty_folder(self):
        ''' test that an empty folder doesn't return any harvestable objects '''
        # FIXME another bad test
        '''
        empty_folder_obj = json.load(open(self.test_nuxeo_empty_folder_object))
        harvestable = self.dh.fetch_harvestable(empty_folder_obj)
        self.assertEqual(len(harvestable), 0)
        '''

if __name__ == '__main__':
    main()
