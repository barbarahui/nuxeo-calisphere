#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from iiif_prezi.factory import ManifestFactory

class IIIFManifest():
    def __init__(self):
        pass

    def create_iiif_manifest(self, object, components=[]):
        '''  Given an object and its components, create a json-ld representation
             compliant with these specs: http://iiif.io/api/presentation/2.1/
        '''
        iiif_manifest_md = {}

        ## manifest: @context
        # descriptive info: label, metadata (pairs), description, thumbnail, attribution, license, logo
        # technical/presentation info: @id, @type, format, height, width, viewingDirection, viewingHint
        # rights info: attribution, license, log
        # links (?)


        ## sequences (for complex objects only?)
        # descriptive info: must have a label if there is more than one sequence, so probably a good default
 
        ## canvas
        # descriptive info: label

        ## content
        
        # paging - for complex objects?
def main(argv=None):
    pass

if __name__ == '__main__':
    sys.exit(main())
