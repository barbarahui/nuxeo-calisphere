#!/usr/bin/env python
import os
import unittest
from deepharvest import mediajson 
import json

class MediaJsonTestCase(unittest.TestCase):

    def setUp(self):
        test_json_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'json')
        self.test_nuxeo_prepped_metadata = os.path.join(test_json_dir, 'nuxeo_prepped_metadata.json')        
        self.test_nuxeo_invalid_object_format = os.path.join(test_json_dir, 'nuxeo_invalid_format.json')
        self.test_component_prepped_md = os.path.join(test_json_dir, 'nuxeo_component_md_prepped.json')

    def test_create_media_json_simple(self):
        ''' Test creating a json representation of object '''
        mj = mediajson.MediaJson()
        nuxeo_md = json.load(open(self.test_nuxeo_prepped_metadata))
        media_json = mj.create_media_json(nuxeo_md)
        self.assertNotIn('structMap', media_json)
        self.assertEqual(media_json['href'], nuxeo_md['href'])
        self.assertEqual(media_json['format'], nuxeo_md['format'])
        self.assertEqual(media_json['label'], nuxeo_md['label'])
        self.assertEqual(media_json['id'], nuxeo_md['id'])
        self.assertEqual(media_json['dimensions'], nuxeo_md['dimensions'])
        self.assertNotIn('extraneous', media_json) 

    def test_create_media_json_complex(self):
        ''' test assembling metadata for a complex object '''
        parent_md = json.load(open(self.test_nuxeo_prepped_metadata))
        component_md = json.load(open(self.test_component_prepped_md))
        mj = mediajson.MediaJson()
        media_json = mj.create_media_json(parent_md, component_md)
        self.assertIn('structMap', media_json)
        self.assertNotIn('extra_field', media_json['structMap'][0])
        self.assertEqual(media_json['structMap'][0]['href'], component_md[0]['href'])
        self.assertEqual(media_json['structMap'][0]['format'], component_md[0]['format'])
        self.assertEqual(media_json['structMap'][0]['label'], component_md[0]['label'])
        self.assertEqual(media_json['structMap'][0]['id'], component_md[0]['id'])
        self.assertEqual(media_json['structMap'][0]['dimensions'], component_md[0]['dimensions'])

        import pprint
        pp = pprint.PrettyPrinter()
        pp.pprint(media_json)


    def test_invalid_format_error(self):
        ''' Test creation of media_json with an invalid object format gives error '''
        mj = mediajson.MediaJson()
        nuxeo_md = json.load(open(self.test_nuxeo_invalid_object_format))
        with self.assertRaises(ValueError):
            media_json = mj.create_media_json(nuxeo_md)

    def test_stash_no_id_error(self):
        ''' Test stashing media.json file with no id property gives error '''

def main():
    unittest.main()

if __name__ == '__main__':
    main() 
