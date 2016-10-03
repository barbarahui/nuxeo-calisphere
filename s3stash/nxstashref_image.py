#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import argparse
from s3stash.nxstashref import NuxeoStashRef
from ucldc_iiif.convert import Convert
import logging

PRECONVERT = ['image/jpeg', 'image/gif', 'image/png']

class NuxeoStashImage(NuxeoStashRef):

    ''' Base class for fetching a Nuxeo image file, converting it to jp2 and stashing it in S3 '''

    def __init__(self, path, bucket='ucldc-private-files/jp2000', region='us-west-2', pynuxrc='~/.pynuxrc', replace=False):
        super(NuxeoStashImage, self).__init__(path, bucket, region, pynuxrc, replace)
 
        self.logger = logging.getLogger(__name__)
        
        self.source_filename = "sourcefile"
        self.source_filepath = os.path.join(self.tmp_dir, self.source_filename)
        self.magick_tiff_filepath = os.path.join(self.tmp_dir, 'magicked.tif')
        self.uncompressed_tiff_filepath = os.path.join(self.tmp_dir, 'uncompressed.tif')
        self.srgb_tiff_filepath = os.path.join(self.tmp_dir, 'srgb.tiff')
        self.prepped_filepath = os.path.join(self.tmp_dir, 'prepped.tiff')

        name, ext = os.path.splitext(self.source_filename)
        self.jp2_filepath = os.path.join(self.tmp_dir, name + '.jp2')

        self.convert = Convert()

    def nxstashref(self):
        ''' download file, convert to iiif-compatible format, and stash on s3 '''

        self.report['converted'] = False
        self.report['stashed'] = False

        # first see if this looks like a valid file to try to convert 
        is_image, image_msg = self._is_image()
        self._update_report('is_image', {'is_image': is_image, 'msg': image_msg})
        self._update_report('precheck', {'pass': False, 'msg': image_msg})
        if not is_image:
            self._remove_tmp()
            return self.report
           
        self.has_file = self.dh.has_file(self.metadata)
        self._update_report('has_file', self.has_file)
        if not self.has_file:
            return self.report

        self.file_info = self._get_file_info(self.metadata) 
        self.source_mimetype = self.file_info['mimetype']
        passed, precheck_msg = self.convert._pre_check(self.source_mimetype)
        self._update_report('precheck', {'pass': passed, 'msg': precheck_msg})
        if not passed:
            self._remove_tmp()
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
        self.source_download_url = self.file_info['url']
        #self.source_filename = self.file_info['filename']
        self.source_filename = 'sourcefile'
        self.source_filepath = os.path.join(self.tmp_dir, self.source_filename)

        self._update_report('source_download_url', self.source_download_url)
        self._update_report('source_mimetype', self.source_mimetype)
        self._update_report('filename', self.source_filename)
        self._update_report('filepath', self.source_filepath)

        # grab the file to convert
        self._download_nuxeo_file()

        # convert to jp2
        converted, jp2_report = self._create_jp2()
        self._update_report('create_jp2', jp2_report) 
        self._update_report('converted', converted)
        if not converted:
            self._remove_tmp()
            return self.report

        # stash in s3
        stashed, s3_report = self._s3_stash(self.jp2_filepath, 'image/jp2')
        self._update_report('s3_stash', s3_report)
        self._update_report('stashed', stashed)
 
        self._remove_tmp()
        return self.report 

    def _is_image(self):
        ''' do a basic check to see if this is an image '''
        # check Nuxeo object type
        try:
            type = self.metadata['type']
        except KeyError:
            msg = "Could not find Nuxeo metadata type for object. Setting nuxeo type to None"
            return False, msg

        if type in ['SampleCustomPicture']:
            msg = "Nuxeo type is {}".format(type)
            return True, msg
        else:
            msg = "Nuxeo type is {}".format(type)
            return False, msg

    def _create_jp2(self):
        ''' convert a local image to a jp2
        '''
        report = {} 

        # prep file for conversion to jp2
        if self.source_mimetype in PRECONVERT:
            preconverted, preconvert_msg = self.convert._pre_convert(self.source_filepath, self.magick_tiff_filepath)
            report['pre_convert'] = {'preconverted': preconverted, 'msg': preconvert_msg}

            tiff_to_srgb, tiff_to_srgb_msg = self.convert._tiff_to_srgb_libtiff(self.magick_tiff_filepath, self.prepped_filepath)
            report['tiff_to_srgb'] = {'tiff_to_srgb': tiff_to_srgb, 'msg': tiff_to_srgb_msg}

        elif self.source_mimetype == 'image/tiff':
            uncompressed, uncompress_msg = self.convert._uncompress_tiff(self.source_filepath, self.uncompressed_tiff_filepath)
            report['uncompress_tiff'] = {'uncompressed': uncompressed, 'msg': uncompress_msg}

            tiff_to_srgb, tiff_to_srgb_msg = self.convert._tiff_to_srgb_libtiff(self.uncompressed_tiff_filepath, self.prepped_filepath)
            report['tiff_to_srgb'] = {'tiff_to_srgb': tiff_to_srgb, 'msg': tiff_to_srgb_msg}

        else:
            msg = "Did not know how to prep file with mimetype {} for conversion to jp2.".format(self.source_mimetype)
            self.logger.warning(msg)
            report['status'] = 'unknown mimetype'
            report['msg'] = "Did not know how to prep file with mimetype {} for conversion to jp2.".format(self.source_mimetype)
            return report

        # convert to sRGB
         

        # create jp2
        converted, jp2_msg = self.convert._tiff_to_jp2(self.prepped_filepath, self.jp2_filepath)
        report['convert_tiff_to_jp2'] = {'converted': converted, 'msg': jp2_msg}

        return converted, report

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
