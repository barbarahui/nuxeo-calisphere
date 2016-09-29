#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import argparse
from s3stash.nxstashref import NuxeoStashRef
import subprocess
import shutil

class NuxeoStashThumb(NuxeoStashRef):
    ''' 
    Class for stashing a thumbnail on S3 for a given Nuxeo doc
    '''
    def __init__(self, path, bucket='static.ucldc.cdlib.org/ucldc-nuxeo-thumb-media', region='us-east-1', pynuxrc='~/.pynuxrc', replace=False):
       super(NuxeoStashThumb, self).__init__(path, bucket, region, pynuxrc, replace)
       self.magick_convert_location = '/usr/local/bin/convert'

    def nxstashref(self):
        return self.nxstashthumb()

    def nxstashthumb(self):
       ''' stash thumbnail version of file on s3 '''
       self._update_report('stashed', False)

       if self.calisphere_type == 'file':
           return self.stash_file_thumb() 
       elif self.calisphere_type == 'video':
           return self.stash_video_thumb() 
       else:
           self._update_report('calisphere_type', self.calisphere_type)
           return self.report

    def stash_file_thumb(self):
        self.has_file = self.dh.has_file(self.metadata)
        self._update_report('has_file', self.has_file)
        if not self.has_file:
            return self.report

        # get file details
        self.file_info = self._get_file_info(self.metadata)
        self.source_download_url = self.file_info['url']
        self.source_mimetype = 'image/png'
        self.source_filename = self.file_info['filename']
        self.source_filename = self.source_filename.replace(' ', '_')
        self.source_filepath = os.path.join(self.tmp_dir, self.source_filename)
        self.thumb_filepath = os.path.join(self.tmp_dir, 'thumb.png')

        self._update_report('source_download_url', self.source_download_url)
        self._update_report('source_mimetype', self.source_mimetype)
        self._update_report('source_filename', self.source_filename)
        self._update_report('source_filepath', self.source_filepath)
        self._update_report('thumb_filepath', self.thumb_filepath)

        # download the file
        self._download_nuxeo_file()

        # create thumbnail
        thumb_created, thumb_msg = self.pdf_to_thumb(self.source_filepath, self.thumb_filepath)
        self._update_report('thumb_created', {'thumb_created': thumb_created, 'msg': thumb_msg})
        if not thumb_created:
            self._remove_tmp()
            return self.report

        # Copy thumb to source. Need to refactor code to not have to do this.
        shutil.copyfile(self.thumb_filepath, self.source_filepath)

        # stash thumbnail in s3
        stashed, s3_report = self._s3_stash(self.source_filepath, self.source_mimetype)
        self._update_report('s3_stash', s3_report)
        self._update_report('stashed', stashed)

        self._remove_tmp()
        return self.report

    def stash_video_thumb(self):
        # check we have a storyboard 
        self.has_storyboard = self.has_storyboard()
        self._update_report('has_storyboard', self.has_storyboard)
        if not self.has_storyboard:
            return self.report

        # get the download url for the 5th storyboard image
        try:
            self.source_download_url = self.metadata['properties']['vid:storyboard'][5]['content']['data'] 
            self.source_download_url = self.source_download_url.replace('/nuxeo/', '/Nuxeo/')
            self._update_report('source_download_url', self.source_download_url)
            self.source_filename = self.metadata['properties']['vid:storyboard'][5]['content']['name']
            self._update_report('source_filename', self.source_filename)
            self.source_mimetype = self.metadata['properties']['vid:storyboard'][5]['content']['mime-type']
            self._update_report('source_mimetype', self.source_mimetype)
        except KeyError:
            raise KeyError("Nuxeo doc metadata does not contain a 5th storyboard element.")

        # download the image 
        self.source_filepath = os.path.join(self.tmp_dir, self.source_filename)
        self._update_report('source_filepath', self.source_filepath) 
        self._download_nuxeo_file() 

        # stash thumbnail in s3
        stashed, s3_report = self._s3_stash(self.source_filepath, self.source_mimetype)
        self._update_report('s3_stash', s3_report)
        self._update_report('stashed', stashed)

        #self._remove_tmp()
        return self.report
    
    def has_storyboard(self):
        try:
            storyboard = self.metadata['properties']['vid:storyboard']
        except KeyError:
            raise KeyError("Nuxeo object metadata does not contain 'vid:storyboard' element. Make sure 'X-NXDocumentProperties' provided in pynux conf includes 'video'")

        if storyboard is None:
            return False
        else:
            return True

    def pdf_to_thumb(self, input_path, output_path):
        '''
           generate thumbnail image for PDF
           use ImageMagick `convert` tool as described here: http://www.nuxeo.com/blog/qa-friday-thumbnails-pdf-psd-documents/
        '''
        try:
            input_string = "{}[0]".format(input_path) # [0] to specify first page of PDF
            subprocess.check_output([self.magick_convert_location,
                "-quiet",
                "-strip",
                "-format", "png",
                "-quality", "75",
                input_string,
                output_path])
            to_thumb = True
            msg = "Used ImageMagic `convert` to convert {} to {}".format(input_path, output_path)
            self.logger.info(msg)
        except subprocess.CalledProcessError, e:
            to_thumb = False
            msg = 'ImageMagic `convert` command failed: {}\nreturncode was: {}\noutput was: {}'.format(e.cmd, e.returncode, e.output)
            self.logger.error(msg)

        return to_thumb, msg


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
