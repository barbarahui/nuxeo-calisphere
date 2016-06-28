# nuxeo-calisphere

Code for prepping content in Nuxeo for Calisphere harvesting. This is known internally as "deep harvesting". This consists of the following steps:

1. Stashing content files on AWS S3 so that [the UCLDC harvesting process](https://github.com/ucldc/harvester) and the Calisphere front-end can find them.
2. Creating a ['media.json' file](https://github.com/ucldc/ucldc-docs/wiki/media.json) for each object, which the Calisphere front-end uses to get information about the structure of objects from Nuxeo (particularly complex objects). 

## Installation

coming soon...
    
## Deep harvest a collection

How to process and stash all necessary content on S3 for deep harvesting a collection:

First, login to registry-stg.cdlib.org and the `registry` role account. Note: you must be on the CDL network to do this, i.e. you may need to login to the CDL bastion server first.

    $ ssh registry-stg.cdlib.org 
    $ sudo su - registry
    
Then, activate the deepharvestenv virtualenv:

    $ cd nuxeo-calisphere
    $ . deepharvestenv/bin/activate
        
Then, say you wanted to stash the collection with a registry ID of 198, and stash **only new** object files:

    $ python s3stash/stash_collection.py 198 # where '198' is the registry ID
    
If you want to do a **clean restash** of all files, even if they already exist on S3:

    $ python s3stash/stash_collection.py 198 --replace
    
You should see some output as the script is running and then a summary of what happened at the end.      
    

