#!/usr/bin/env python
# -*- coding: utf-8 -*-

from iiif_prezi.factory import ManifestFactory

fac = ManifestFactory()
# Where the resources live on the web
fac.set_base_prezi_uri("http://www.example.org/path/to/object/")
# Where the resources live on disk
fac.set_base_prezi_dir("/usr/local/nuxeo-calisphere/")

# Default Image API information
fac.set_base_image_uri("http://pottoloris-env.elasticbeanstalk.com/")
fac.set_iiif_image_info(2.0, 2) # Version, ComplianceLevel

# 'warn' will print warnings, default level
# 'error' will turn off warnings
# 'error_on_warning' will make warnings into errors
fac.set_debug("warn") 

manifest = fac.manifest(label="Example Manifest")
manifest.set_metadata({"Date": "Some Date", "Location": "Some Location"})
manifest.description = "This is a longer description of the manifest"
manifest.viewingDirection = "left-to-right"

seq = manifest.sequence()

cvs = seq.canvas(ident="page-1", label="Page 1")
cvs.set_image_annotation("a4a8937b-2cc3-42ea-935e-2bfdb311a4ba", iiif=True)
cvs = seq.canvas(ident="page-2", label="Page 2")
cvs.set_image_annotation("a4a8937b-2cc3-42ea-935e-2bfdb311a4ba", iiif=True)

manifest.toFile(compact=False)
