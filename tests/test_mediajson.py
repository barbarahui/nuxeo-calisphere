#!/usr/bin/env python
import unittest
from deepharvest import mediajson 

FILE_FORMATS = ['image', 'audio', 'video', 'file']

class MediaJsonTestCase(unittest.TestCase):

    def testContentDivision(self):
        ''' Test creation of content division for media.json content '''
        href = "https://nuxeo.cdlib.org/path/to/image.tiff"
        id = "4430a193-dba3-4701-8eb7-f53769a77449"
        label = "A Yellow Bird"
        dimensions = "1024:1024"
        dh = mediajson.MediaJson()
        content_div = dh.content_division(id, href, label, dimensions)
        self.assertEqual(content_div['href'], href)
        self.assertEqual(content_div['id'], id)
        self.assertEqual(content_div['label'], label)
        self.assertEqual(content_div['dimensions'], dimensions)
        self.assertEqual(content_div['format'], 'image')

    def testCreateJsonFile(self):
        ''' Test creation of media.json file '''
        pass

    def testS3Stash(self):
        ''' Test stashing of media.json file on S3 ''' 
        pass

def main():
    unittest.main()

if __name__ == '__main__':
    main() 
