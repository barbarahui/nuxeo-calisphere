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

    def test_create_media_json(self):
        ''' Test creating a json representation of object '''
        mj = mediajson.MediaJson()
        nuxeo_md = json.load(open(self.test_nuxeo_prepped_metadata))
        media_json = mj.create_media_json(nuxeo_md)
        self.assertEqual(media_json['href'], nuxeo_md['href'])
        self.assertEqual(media_json['format'], nuxeo_md['format'])
        self.assertEqual(media_json['label'], nuxeo_md['label'])
        self.assertEqual(media_json['id'], nuxeo_md['id'])
        self.assertEqual(media_json['dimensions'], nuxeo_md['dimensions'])
        self.assertNotIn('extraneous', media_json) 

    def test_invalid_format_error(self):
        ''' Test creation of media_json with an invalid object format fails '''
        mj = mediajson.MediaJson()
        nuxeo_md = json.load(open(self.test_nuxeo_invalid_object_format))
        with self.assertRaises(ValueError):
            media_json = mj.create_media_json(nuxeo_md)

def main():
    unittest.main()

if __name__ == '__main__':
    main() 
