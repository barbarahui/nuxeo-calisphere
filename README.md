# nuxeo-calisphere

Code for prepping content in Nuxeo for Calisphere harvesting. This is known internally as "deep harvesting". This consists of the following steps:

1. Stashing content files on AWS S3 so that [the UCLDC harvesting process](https://github.com/ucldc/harvester) and the Calisphere front-end can find them.
2. Creating a ['media.json' file](https://github.com/ucldc/ucldc-docs/wiki/media.json) for each object, which the Calisphere front-end uses to get information about the structure of objects from Nuxeo (particularly complex objects). 

## Installation

requires ffmpeg and ffprobe

Because it uses the ucldc-iiif project it also requires ImageMagick, libtiff and kakadu.
    
See https://github.com/mredar/ingest_deploy/blob/master/ansible/roles/worker/tasks/install_deep_harvester.yml for an Ansible playbook that installs this code.

## Deep harvest a collection

As of December 2016, the harvester worker machines can now run the deep harvesting code. The deep harvest has been added as an "action" in the registry admin tool. The process will create a Slack message with the summary report for the run.

The more detailed json reports are now stored on S3. The location is:

`https://s3.amazonaws.com/static.ucldc.cdlib.org/deep-harvesting/reports/{report_type}-{collection id}.json`

Where the {report_type} is one of "files", "images", "thumbs" or "mediajson" and the {collection id} is the registry numeric ID for the collection.

### Old registry deep harvest procedure

How to process and stash all necessary content on S3 for deep harvesting a collection:

First, login to registry-stg.cdlib.org and the `registry` role account. Note: you must be on the CDL network to do this, i.e. you may need to login to the CDL bastion server first.

    $ ssh registry-stg.cdlib.org 
    $ sudo su - registry
    
Then, activate the deepharvestenv virtualenv:

    $ cd nuxeo-calisphere
    $ . deepharvestenv/bin/activate
        
Then, say you wanted to stash the collection with a registry ID of 198, and stash **only new** object files:

    $ python s3stash/stash_collection.py --pynuxrc ~/.pynuxrc-prod 198 # where '198' is the registry ID
    
If you want to do a **clean restash** of all files, even if they already exist on S3:

    $ python s3stash/stash_collection.py --pynuxrc ~/.pynuxrc-prod 198 --replace
    
You should see some output as the script is running and then a summary of what happened at the end.      

### Running deep harvest for a large collection

If you're running a deep harvest for a very large collection with lots of files to stash, you might want to use the **atnow** script so that you don't have to worry about the terminal hanging up on you while the job is in process.

Note: right now there is a problem setting the environment variables correctly when using atnow. BH is trying to figure it out -- ask her if it's working yet :-)    

