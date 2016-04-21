#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import argparse
from s3stash.nxstashref import NuxeoStashRef

VALID_CALISPHERE_TYPES = ['file', 'audio', 'video']

class NuxeoStashFile(NuxeoStashRef):
    ''' 
        Class for fetching a Nuxeo object file and stashing in S3
    '''
    def __init__(self, path, bucket='ucldc-nuxeo-ref-media', region='us-west-2', pynuxrc='~/.pynuxrc', replace=False):
        super(NuxeoStashFile, self).__init__(path, bucket, region, pynuxrc, replace)
        
    def nxstashref(self):
        ''' download file and stash in s3 ''' 

        self.report['stashed'] = False

        if not self.calisphere_type in VALID_CALISPHERE_TYPES:
            self._update_report('valid_type', False)
            return self.report

        self.has_file = self.dh.has_file(self.metadata)
        self._update_report('has_file', self.has_file)
        if not self.has_file:
            return self.report 

        self.s3_stashed = self._is_s3_stashed()
        self._update_report('already_s3_stashed', self.s3_stashed)
        if not self.replace and self.s3_stashed:
            return self.report 

        # get file details 
        self.file_info = self._get_file_info(self.metadata)
        self.source_download_url = self.file_info['url']
        self.source_mimetype = self.file_info['mimetype']
        self.source_filename = self.file_info['filename']
        self.source_filepath = os.path.join(self.tmp_dir, self.source_filename)

        self._update_report('source_download_url', self.source_download_url)
        self._update_report('source_mimetype', self.source_mimetype)
        self._update_report('filename', self.source_filename)
        self._update_report('filepath', self.source_filepath)

        # download the file
        self._download_nuxeo_file() 

        # stash in s3
        stashed, s3_report = self._s3_stash()
        self._update_report('s3_stash', s3_report)
        self._update_report('stashed', stashed)

        # remove temp files
        self._remove_tmp()

        return self.report

def main(argv=None):
    pass

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
