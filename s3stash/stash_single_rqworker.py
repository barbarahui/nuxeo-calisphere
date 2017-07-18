# a module for stashing single nuxeo objects from the rq workers
import json
from s3stash.publish_to_harvesting import publish_to_harvesting
from s3stash.nxstashref_file import NuxeoStashFile
from s3stash.nxstashref_image import NuxeoStashImage
from s3stash.nxstash_mediajson import NuxeoStashMediaJson
from s3stash.nxstash_thumb import NuxeoStashThumb


def stash_file(path):
    '''Stash a single file to s3'''
    bucket = 'ucldc-nuxeo-ref-media'
    region = 'us-west-2'
    pynuxrc = '~/.pynuxrc'
    replace = True
    nxstash = NuxeoStashFile(
        unicode(path, "utf-8"), bucket, region, pynuxrc, replace)
    report = nxstash.nxstashref()
    publish_to_harvesting('Stashed file for {}'.format(path),
                          json.dumps(report))


def stash_image(path):
    '''Stash a single image to s3'''
    bucket = 'ucldc-private-files/jp2000'
    region = 'us-west-2'
    pynuxrc = '~/.pynuxrc'
    replace = True
    nxstash = NuxeoStashImage(
        unicode(path, "utf-8"), bucket, region, pynuxrc, replace)
    report = nxstash.nxstashref()
    publish_to_harvesting('Stashed image for {}'.format(path),
                          json.dumps(report))


def stash_media_json(path):
    '''Stash media json for object'''

    bucket = 'static.ucldc.cdlib.org/media_json'
    region = 'us-west-2'
    pynuxrc = '~/.pynuxrc'
    replace = True
    nxstash = NuxeoStashMediaJson(path, bucket, region, pynuxrc, replace)
    report = nxstash.nxstashref()
    publish_to_harvesting('Stashed media_json for {}'.format(path),
                          json.dumps(report))


def stash_thumb(path):
    '''Stash single thumb'''
    bucket = 'static.ucldc.cdlib.org/ucldc-nuxeo-thumb-media'
    region = 'us-west-2'
    pynuxrc = '~/.pynuxrc'
    replace = True
    nxstash = NuxeoStashThumb(
        unicode(path, "utf-8"), bucket, region, pynuxrc, replace)
    report = nxstash.nxstashref()
    publish_to_harvesting('Stashed thumb for {}'.format(path),
                          json.dumps(report))
