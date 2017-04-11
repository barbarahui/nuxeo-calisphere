#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from s3stash.nxstashref import NuxeoStashRef
from deepharvest.deepharvest_nuxeo import DeepHarvestNuxeo
from deepharvest.mediajson import MediaJson
from dplaingestion.mappers.ucldc_nuxeo_mapper import UCLDCNuxeoMapper
import json
import s3stash.s3tools

FILENAME_FORMAT = "{}-media.json"


class NuxeoStashMediaJson(NuxeoStashRef):
    ''' create and stash media.json file for a nuxeo object '''

    def __init__(self,
                 path,
                 bucket,
                 region,
                 pynuxrc='~/.pynuxrc',
                 replace=True):
        print type(path)
        super(NuxeoStashMediaJson, self).__init__(path, bucket, region,
                                                  pynuxrc, replace)

        self.dh = DeepHarvestNuxeo(
            self.path, self.bucket, pynuxrc=self.pynuxrc)
        self.mj = MediaJson()

        self.filename = FILENAME_FORMAT.format(self.uid)
        self.filepath = os.path.join(self.tmp_dir, self.filename)
        self._update_report('filename', self.filename)
        self._update_report('filepath', self.filepath)

    def nxstashref(self):
        return self.nxstash_mediajson()

    def nxstash_mediajson(self):
        ''' create media.json file for object and stash on s3 '''
        self._update_report('stashed', False)

        # extract and transform metadata for parent obj and any components
        parent_md = self._get_parent_metadata(self.metadata)
        component_md = [
            self._get_component_metadata(c)
            for c in self.dh.fetch_components(self.metadata)
        ]

        # create media.json file
        media_json = self.mj.create_media_json(parent_md, component_md)
        self._write_file(media_json, self.filepath)

        # stash media.json file on s3
        stashed, s3_report = s3stash.s3tools.s3stash(
            self.filepath, self.bucket, self.filename, self.region,
            'application/json', self.replace)
        self._update_report('s3_stash', s3_report)
        self._update_report('stashed', stashed)

        self._remove_tmp()

        return self.report

    def _get_parent_metadata(self, obj):
        ''' assemble top-level (parent) object metadata '''
        metadata = {}
        metadata['label'] = obj['title']

        # only provide id, href, format if Nuxeo Document has file attached
        full_metadata = self.nx.get_metadata(uid=obj['uid'])

        if self.dh.has_file(full_metadata):
            metadata['id'] = obj['uid']
            metadata['href'] = self.dh.get_object_download_url(full_metadata)
            metadata['format'] = self.dh.get_calisphere_object_type(obj[
                'type'])
            if metadata['format'] == 'video':
                metadata['dimensions'] = self.dh.get_video_dimensions(
                    full_metadata)

        return metadata

    def _get_component_metadata(self, obj):
        ''' assemble component object metadata '''
        metadata = {}
        full_metadata = self.nx.get_metadata(uid=obj['uid'])
        metadata['label'] = obj['title']
        metadata['id'] = obj['uid']
        metadata['href'] = self.dh.get_object_download_url(full_metadata)

        # extract additional  ucldc metadata from 'properties' element
        ucldc_md = self._get_ucldc_schema_properties(full_metadata)

        for key, value in ucldc_md.iteritems():
            metadata[key] = value

        # map 'type'
        metadata['format'] = self.dh.get_calisphere_object_type(obj['type'])

        return metadata

    def _get_ucldc_schema_properties(self, metadata):
        ''' get additional metadata as mapped by harvester '''
        properties = {}

        mapper = UCLDCNuxeoMapper(metadata)
        mapper.map_original_record()
        mapper.map_source_resource()

        properties = mapper.mapped_data['sourceResource']
        properties.update(mapper.mapped_data['originalRecord'])

        return properties

    def _write_file(self, content_dict, filepath):
        """ convert dict to json and write to file """
        content_json = json.dumps(
            content_dict, indent=4, separators=(',', ': '), sort_keys=False)
        with open(filepath, 'wb') as f:
            f.write(content_json)
            f.flush()


def main(argv=None):
    pass


if __name__ == "__main__":
    sys.exit(main())
