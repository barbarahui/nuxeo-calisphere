import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="UCLDC Deep Harvester",
    version="0.0.4",
    description=("deep harvester code for the UCLDC project"),
    long_description=read('README.md'),
    author='Barbara Hui',
    author_email='barbara.hui@ucop.edu',
    dependency_links=[
        'https://github.com/ucldc/pynux/archive/master.zip#egg=pynux',
        'https://github.com/mredar/jsonpath/archive/master.zip#egg=jsonpath',
        'https://github.com/barbarahui/ucldc-iiif/archive/master.zip#egg=ucldc-iiif'
    ],
    # pinning versions here for ingest_deploy as a stopgap until we are moved to python3
    install_requires=[
        'argparse',
	'boto==2.49.0',
        'boto3==1.9.160',
        'pynux',
        'python-magic==0.4.15',
        'couchdb==0.9',
        'jsonpath==0.54',
	'akara==2.0.0a4',
        'ucldc-iiif'
    ],
    packages=['deepharvest', 's3stash'],
    test_suite='tests'
)
### note: dpla-ingestion code is a dependency
###pip_main(['install',
###         'git+ssh://git@bitbucket.org/mredar/dpla-ingestion.git@ucldc'])
