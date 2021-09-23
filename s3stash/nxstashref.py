#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from pynux import utils
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import tempfile
import logging
import shutil
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
import urllib
from os.path import expanduser
import s3stash.s3tools

S3_URL_FORMAT = "s3://{0}/{1}"


class NuxeoStashRef(object):
    ''' Base class for fetching a Nuxeo file and stashing it in S3 '''

    def __init__(self,
                 path,
                 bucket,
                 region,
                 pynuxrc='~/.pynuxrc',
                 replace=False, **kwargs):

        self.logger = logging.getLogger(__name__)

        self.path = path
        self.bucket = bucket
        self.pynuxrc = pynuxrc
        self.region = region
        self.replace = replace

        self.nx = utils.Nuxeo(rcfile=open(expanduser(self.pynuxrc), 'r'))

        if 'metadata' in kwargs:
            self.metadata = kwargs['metadata']
            self.logger.info("got metadata from kwargs")
        else:
            self.metadata = self.nx.get_metadata(path=self.path)   
            self.logger.info("got metadata via pynux utils")

        self.uid = self.metadata['uid']

        self.logger.info("initialized NuxeoStashRef with path {}".format(
            self.path.encode('ascii', 'replace')))

        self.dh = DeepHarvestNuxeo(self.path, uid=self.uid)
        self.calisphere_type = self.dh.get_calisphere_object_type(
            self.metadata['type'])
        self.tmp_dir = tempfile.mkdtemp(dir='/tmp')  # FIXME put in conf

        self.report = {}
        self._update_report('uid', self.uid)
        self._update_report('path', self.path)
        self._update_report('bucket', self.bucket)
        self._update_report('replace', self.replace)
        self._update_report('pynuxrc', self.pynuxrc)
        self._update_report('calisphere_type', self.calisphere_type)

    def nxstashref(self):
        ''' download, prep and stash file '''
        raise NotImplementedError

    def _update_report(self, key, value):
        ''' add a key/value pair to report dict '''
        self.report[key] = value

    def _remove_tmp(self):
        ''' clean up after ourselves '''
        shutil.rmtree(self.tmp_dir)

    def _download_nuxeo_file(self):

        # https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/#retry-on-failure
        retry_strategy = Retry(
            total=3,
            status_forcelist=[413, 429, 500, 502, 503, 504],
)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        #response = http.get("https://en.wikipedia.org/w/api.php")

        # https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        res = http.get(self.source_download_url,
                           headers=self.nx.document_property_headers,
                           auth=self.nx.auth, stream=True, timeout=1, 3)
        '''
        res = requests.get(self.source_download_url,
                           headers=self.nx.document_property_headers,
                           auth=self.nx.auth, stream=True)
        '''
        res.raise_for_status()
        with open(self.source_filepath, 'wb') as f:
            for block in res.iter_content(chunk_size=None):
                f.write(block)
        self.logger.info("Downloaded file from {} to {}".format(
            self.source_download_url, self.source_filepath))

    def _get_file_info(self, metadata):
        ''' given the full metadata for an object, get file download url '''
        info = {}

        # for videos, try to get nuxeo transcoded video file url first
        if metadata['type'] == 'CustomVideo':
           try:
               transcoded_video = metadata['properties']['vid:transcodedVideos']
               for tv in transcoded_video:
                  if tv['content']['mime-type'] == 'video/mp4':
                     url = tv['content']['data']
                     url = url.replace('/nuxeo/', '/Nuxeo/')
                     info['url'] = url.strip()
                     info['mimetype'] = tv['content']['mime-type'].strip()
                     info['filename'] = tv['content']['name'].strip()
                     return info
           except KeyError:
               pass

        try:
            file_content = metadata['properties']['file:content']
        except KeyError:
            raise KeyError(
                "Nuxeo object metadata does not contain 'properties/file:"
                "content' element. Make sure 'X-NXDocumentProperties' "
                "provided in pynux conf includes 'file'"
            )

        if file_content is None:
            return None
        else:
            url = file_content['data'].strip()
            url = url.replace('/nuxeo/', '/Nuxeo/')
            info['url'] = url.strip()
            info['mimetype'] = file_content['mime-type'].strip()
            info['filename'] = file_content['name'].strip()

        if not info['filename']:
            try:
                info['filename'] = metadata['properties']['file:filename']
            except KeyError:
                raise KeyError(
                    "Nuxeo object metadata does not contain 'properties/file:"
                    "filename' element. Make sure 'X-NXDocumentProperties' "
                    "provided in pynux conf includes 'file'"
                )

        return info

    def _is_s3_stashed(self):
        """ Check for existence of key on S3.
       """
        return s3stash.s3tools.is_s3_stashed(self.bucket, self.uid,
                                             self.region)

    def _s3_stash(self, filepath, mimetype):
        """ Stash file in S3 bucket.
       """
        return s3stash.s3tools.s3stash(filepath, self.bucket, self.uid,
                                       self.region, mimetype, self.replace)


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
