#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os
from s3stash.nxstashref import NuxeoStashRef
import subprocess
import shutil


class NuxeoStashThumb(NuxeoStashRef):
    '''
        Class for fetching a Nuxeo object of type `SampleCustomFile`,
        creating a thumbnail image of the file, and stashing in S3.
    '''

    def __init__(self,
                 path,
                 bucket='static.ucldc.cdlib.org/ucldc-nuxeo-thumb-media',
                 region='us-east-1',
                 pynuxrc='~/.pynuxrc',
                 replace=False,
                 **kwargs):
        super(NuxeoStashThumb, self).__init__(path, bucket, region, pynuxrc,
                                              replace, **kwargs)
        self.magick_convert_location = os.environ.get('PATH_MAGICK_CONVERT',
                                                      '/usr/local/bin/convert')
        self.ffmpeg_location = os.environ.get('PATH_FFMPEG',
                                              '/usr/local/bin/ffmpeg')
        self.ffprobe_location = os.environ.get('PATH_FFPROBE',
                                               '/usr/local/bin/ffprobe')

    def nxstashref(self):
        return self.nxstashthumb()

    def nxstashthumb(self):
        ''' stash thumbnail version of file on s3 '''
        self._update_report('stashed', False)

        if self.calisphere_type not in ('file', 'video'):
            self._update_report('calisphere_type', self.calisphere_type)
            return self.report

        self.has_file = self.dh.has_file(self.metadata)
        self._update_report('has_file', self.has_file)
        if not self.has_file:
            return self.report

        # get file details
        self.file_info = self._get_file_info(self.metadata)
        self.source_download_url = self.file_info['url']
        if self.calisphere_type == 'file':
            self.source_mimetype = 'image/png'
        elif self.calisphere_type == 'video':
            self.source_mimetype = 'image/jpg'

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
        if self.calisphere_type == 'file':
            thumb_created, thumb_msg = self.pdf_to_thumb(self.source_filepath,
                                                         self.thumb_filepath)
        elif self.calisphere_type == 'video':
            thumb_created, thumb_msg = self.video_to_thumb(
                self.source_filepath, self.thumb_filepath)

        self._update_report('thumb_created',
                            {'thumb_created': thumb_created,
                             'msg': thumb_msg})
        if not thumb_created:
            self._remove_tmp()
            return self.report

        # Copy thumb to source. Need to refactor code to not have to do this.
        shutil.copyfile(self.thumb_filepath, self.source_filepath)

        # stash thumbnail in s3
        stashed, s3_report = self._s3_stash(self.source_filepath,
                                            self.source_mimetype)
        self._update_report('s3_stash', s3_report)
        self._update_report('stashed', stashed)

        self._remove_tmp()

        return self.report

    def video_to_thumb(self, input_path, output_path):
        '''
           generate thumbnail image for video
           use ffmpeg to grab center frame from video
        '''
        to_thumb = False

        try:
            duration = subprocess.check_output([
                self.ffprobe_location,
                '-v',
                'fatal',
                '-show_entries',
                'format=duration',
                '-of',
                'default=nw=1:nk=1',
                input_path],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            msg = 'ffprobe check failed: {}\nreturncode ' \
                  'was: {}\noutput was: {}'.format(e.cmd,
                                                   e.returncode,
                                                   e.output)
            self.logger.error(msg)

        midpoint = float(duration.strip()) / 2

        try:
            subprocess.check_output([
                self.ffmpeg_location,
                '-v',
                'fatal',
                '-ss',
                str(midpoint),
                '-i',
                input_path,
                '-vframes',
                '1',  # output 1 frame
                output_path],
                stderr=subprocess.STDOUT)
            to_thumb = True
            msg = "Used ffmpeg to convert {} to {}".format(
                input_path, output_path)
            self.logger.info(msg)
        except subprocess.CalledProcessError, e:
            to_thumb = False
            msg = 'ffmpeg thumbnail creation failed: {}\nreturncode ' \
                  'was: {}\noutput was: {}'.format(e.cmd,
                                                   e.returncode,
                                                   e.output)
            self.logger.error(msg)
        return to_thumb, msg

    def pdf_to_thumb(self, input_path, output_path):
        '''
           generate thumbnail image for PDF
           use ImageMagick `convert` tool as described here:
           http://www.nuxeo.com/blog/qa-friday-thumbnails-pdf-psd-documents/
        '''
        to_thumb = False
        try:
            input_string = "{}[0]".format(
                input_path)  # [0] to specify first page of PDF
            subprocess.check_output([
                self.magick_convert_location,
                "-quiet",
                "-strip",
                "-format",
                "png",
                "-quality",
                "75",
                input_string,
                output_path],
                stderr=subprocess.STDOUT)
            to_thumb = True
            msg = "Used ImageMagic `convert` to convert {} to {}".format(
                input_path, output_path)
            self.logger.info(msg)
        except subprocess.CalledProcessError, e:
            msg = 'ImageMagic `convert` command failed: {}\nreturncode ' \
                  'was: {}\noutput was: {}'.format(e.cmd,
                                                   e.returncode,
                                                   e.output)
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
