# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 09:03:51 2015

@author: home

Code to check mentions ids in timeline data...

"""

import ConfigParser
import datetime
from datetime import timedelta 
from pymongo import Connection
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt 


 
#config = ConfigParser.ConfigParser()
#config.read('scraper.cfg')
 
# spin up database
#DBNAME = config.get('database', 'name')
#COLLECTION = config.get('database', 'collection')

DBNAME = 'twitter_test'
COLLECTION = 'home_timelines'

print(DBNAME)
print(COLLECTION)

conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

print("twitter connection and database connection configured")

username = 'needingbones'
username = 'anasecretss'
username = 'tiinyterry'

results = tweets.find({'user.screen_name': username})
for result in results:
    # result['in_reply_to_screen_name'] + "\t" + result['in_reply_to_user_id']
    for entity in result['entities']['user_mentions']:
        print str(entity['id_str']) +"\t"+ str(entity['id']) +"\t"+ str(entity['screen_name'])






#results = tweets.find({'user.screen_name': u'AdesimboAdedeji'})
#for result in results:
#    print result
