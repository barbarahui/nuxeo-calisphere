import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="UCLDC Deep Harvester",
    version="0.0.3",
    description=("deep harvester code for the UCLDC project"),
    long_description=read('README.md'),
    author='Barbara Hui',
    author_email='barbara.hui@ucop.edu',
    dependency_links=[
        'https://github.com/ucldc/pynux/archive/master.zip#egg=pynux',
        'https://github.com/mredar/jsonpath/archive/master.zip#egg=jsonpath',
        'https://github.com/barbarahui/ucldc-iiif/archive/master.zip#egg=ucldc-iiif'
    ],
    install_requires=[
        'argparse',
        'boto',
        'boto3',
        'pynux',
        'python-magic',
        'couchdb',
        'jsonpath',
        'akara',
        'ucldc-iiif'
    ],
    packages=['deepharvest', 's3stash'],
    test_suite='tests'
)
### note: dpla-ingestion code is a dependency
###pip_main(['install',
###         'git+ssh://git@bitbucket.org/mredar/dpla-ingestion.git@ucldc'])
