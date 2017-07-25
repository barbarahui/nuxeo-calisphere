#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os
from s3stash.nxstashref import NuxeoStashRef
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
from deepharvest.iiif_manifest import IIIFManifest 
from iiif_prezi.factory import ManifestFactory

FILENAME_FORMAT = "{}-iiif-manifest.json"

class NuxeoStashIIIFManifest(NuxeoStashRef):
    '''  create and stash IIIF manifest for a nuxeo object '''

    def __init__(self,
                 path,
                 bucket,
                 region,
                 pynuxrc='~/.pynuxrc',
                 replace=True):
        super(NuxeoStashIIIFManifest, self).__init__(path, bucket, region,
                                                  pynuxrc, replace)

        self.dh = DeepHarvestNuxeo(
            self.path, self.bucket, pynuxrc=self.pynuxrc)
        self.iiif = IIIFManifest()
 
        self.filename = FILENAME_FORMAT.format(self.uid)
        self.filepath = os.path.join(self.tmp_dir, self.filename)
        self._update_report('filename', self.filename)
        self._update_report('filepath', self.filepath)

    def nxstashref(self):
        return self.nxstash_iiif_manifest()

    def nxstash_iiif_manifest(self):
        ''' create IIIF manifest file for object and stash on S3 '''
        self._update_report('stashed', False)

        # extract and transform metadata for parent obj and any components
        #parent_md = self._get_parent_metadata(self.metadata)
        #    self._get_component_metadata(c)
        #    for c in self.dh.fetch_components(self.metadata)
        #]

        # do we just want to stuff all of the ucldc_schema metadata into the manifest? is there any harm in doing so? what about namespacing?

        

        return self.report

def main(argv=None):
    pass


if __name__ == "__main__":
    sys.exit(main())

