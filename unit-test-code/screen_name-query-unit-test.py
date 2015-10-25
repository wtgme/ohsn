# -*- coding: utf-8 -*-
"""
Created on Thu Jun 04 10:24:15 2015

@author: home
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:29:37 2015

Initial code purloined from the example at: https://unsupervisedlearning.wordpress.com/

@author: home

Its been modified to collect a users friends and followers

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


#usernames = {'anasecretss':'r-', 'needingbones':'b-', 'tiinyterry':'g-'}

username = 'anasecretss'

results = tweets.find({'user.screen_name': username})
for result in results:
    print result['text'].encode('utf-8')

#results = tweets.find({'user.screen_name': u'AdesimboAdedeji'})
#for result in results:
#    print result