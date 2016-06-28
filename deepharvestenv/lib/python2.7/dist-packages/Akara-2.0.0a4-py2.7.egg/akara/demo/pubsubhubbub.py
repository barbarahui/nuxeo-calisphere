# -*- encoding: utf-8 -*-
'''
PubSubHubbub

See also:

http://code.google.com/p/pubsubhubbub/
http://pubsubhubbub.googlecode.com/svn/trunk/pubsubhubbub-core-0.3.html

Requires a configuration section, for example:

[pubsubhubbub]

entries = /path/to/entry/files/*.atom
feed_envelope = <feed xmlns="http://www.w3.org/2005/Atom"><title>My feed</
title><id>http://example.com/myfeed</id></feed>

'''

import sys
from datetime import datetime, timedelta
import cgi
import sqlite3
from itertools import dropwhile

import amara
from amara import bindery
from amara.tools import atomtools
from amara.thirdparty import httplib2
from amara.lib.util import first_item

from akara.services import simple_service
from akara import request, response
from akara import logger

#akara.util.pubsubhubbub provides tools for creating subscribers

DBFILE = AKARA.module_config['dbfile']

#http://copia.posterous.com/quotidie-eliot-milton-and-ars-versificandi

def ensuredb():
    logger.debug('DBFILE: ' + repr(DBFILE))
    db = sqlite3.connect(DBFILE)
    try:
        db.execute("select count(*) from subscription")
    except sqlite3.OperationalError:
        # Create table
        #db.execute('''create table subscriber
        #(topic text, callback text, added timestamp)''')
        db.execute('''create table subscription
        (callback text, topic text, added timestamp)''')
        #(topic text, latlong text, city text, state text, country text, updated timestamp)''')
        db.commit()
    return db


def dict2obj(d):
    '''
    >>> p = dict2obj({'spam': 1, 'eggs': 2, 'bacon': 0})
    >>> p.spam
    1
    >>> p.eggs
    2
    '''
    #FIXME: use Bindery rules for handling problem dict keys
    class oclass(object): pass
    o = oclass()
    for k, v in d.iteritems():
        setattr(o, k, v)
    return o


SERVICE_ID = 'http://purl.org/akara/services/demo/pubsubhubbub.sub'
@simple_service('POST', SERVICE_ID, 'akara.pubsubhubbub.sub')
def pubsubhubbub_sub(body, ctype):
    '''
    Sample requests:
    * curl --data "mode=subscribe&callback=http%3A%2F%2Flocalhost%3A8880%2Fpshbtestcb&topic=http%3A%2F%2Flocalhost%3A8880%2Fpshbtesttop" "http://localhost:8880/akara.pubsubhubbub.sub"

    sqlite3 /tmp/pubsubhubbub.db 'select * from subscription;'

    '''
    
    '''
    import httplib, urllib
    params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0}) #-> application/x-www-form-urlencoded
    '''
    logger.debug('parsed: ' + repr(dict(cgi.parse_qsl(body))))
    hub = dict2obj(dict(cgi.parse_qsl(body)))
    db = ensuredb()
    if hub.mode == 'unsubscribe':
        resp = db.execute("delete from subscription where callback=? and topic=?", (hub.callback, hub.topic))
        logger.debug('accepted_imts: unsubscribe' + repr(resp))
        db.commit()
    elif hub.mode == 'subscribe':
        resp = db.execute("insert into subscription values (?, ?, ?)", (hub.callback, hub.topic, datetime.now(),))
        logger.debug('accepted_imts: subscribe' + repr(resp))
        db.commit()

    #hub.verify
    #hub.lease_seconds
    #hub.secret
    #hub.verify_token
    response.code = 204 #Or 202 for deferred verification
    return ''


@simple_service('POST', SERVICE_ID, 'akara.pubsubhubbub.hub')
def pubsubhubbub_hub(body, ctype):
    '''
    Sample requests:
    * curl --data "mode=subscribe&callback=http%3A%2F%2Flocalhost%3A8880%2Fpshbtestcb&topic=http%3A%2F%2Flocalhost%3A8880%2Fpshbtesttop" "http://localhost:8880/akara.pubsubhubbub.hub"
    * curl --data "mode=publish&callback=http%3A%2F%2Flocalhost%3A8880%2Fpshbtestcb&topic=http%3A%2F%2Flocalhost%3A8880%2Fpshbtesttop" "http://localhost:8880/akara.pubsubhubbub.hub"
    '''
    logger.debug('parsed: ' + repr(dict(cgi.parse_qsl(body))))
    hub = dict2obj(dict(cgi.parse_qsl(body)))
    db = ensuredb()
    if hub.mode == 'subscribe':
        #Request from a subscriber to subscribe to a topic of interest
        resp = db.execute("insert into subscription values (?, ?, ?)", (hub.callback, hub.topic, datetime.now(),))
        logger.debug('accepted_imts: subscribe' + repr(resp))
        db.commit()

    if hub.mode == 'publish':
        #Ping notification from a publisher whose topics have changed.
        resp = db.execute("insert into subscription values (?, ?, ?)", (hub.callback, hub.topic, datetime.now(),))
        logger.debug('accepted_imts: subscribe' + repr(resp))
        db.commit()

    #hub.verify
    #hub.lease_seconds
    #hub.secret
    #hub.verify_token
    response.code = 204 #Or 202 for deferred verification
    return ''


