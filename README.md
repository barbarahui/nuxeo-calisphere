# nuxeo-calisphere

Scripts for "deep harvesting" content from the UCLDC Nuxeo instance, which essentially entails:

1. Stashing content files on AWS S3 so that [the UCLDC harvesting process](https://github.com/ucldc/harvester) and the Calisphere front-end can find them. Note: right now, the scripts in this repo only deal with non-image content (i.e. pdf, audio, video). The scripts in [ucldc-iiif](https://github.com/barbarahui/ucldc-iiif) deal with images.
2. Creating a ['media.json' file](https://github.com/ucldc/ucldc-docs/wiki/media.json) for each object, which the Calisphere front-end uses to get information about the structure of objects from Nuxeo (particularly complex objects). 

## Installation

Clone this repo as per usual, e.g.:

    https://github.com/barbarahui/nuxeo-calisphere.git
    
Install system dependencies:

- libmagic
- imagemagick
- ghostscript

Install the nuxeo-calisphere python package:

     $ cd nuxeo-calisphere
     $ python setup.py install

Create a couple of directories:

    $ mkdir reports
    $ mkdir logs

You can try running the tests, but tbh they need rewriting to not be network dependent or dependent on real data, which means they will likely fail:

    $ python setup.py test
    
## S3 Stash content files for a collection

Note: right now, the scripts in this repo only deal with stashing non-image content (i.e. pdf, audio, video). The scripts in [ucldc-iiif](https://github.com/barbarahui/ucldc-iiif) deal with images, which need a lot more processing.

How to stash content files and thumbnails for a collection (substitute the path to the Nuxeo collection you want):

    $ cd nuxeo-calisphere
    $ python s3stash/stash_collection_files.py /asset-library/UCM/NightingaleDiaries
    $ python s3stash/stash_collection_thumbs.py /asset-library/UCM/NightingaleDiaries
    
## Create media.json files for a collection and stash on S3

    $ cd nuxeo-calisphere
    $ python deepharvest/deepharvest_nuxeo.py /asset-library/UCM/NightingaleDiaries
    

    