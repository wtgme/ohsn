# -*- coding: utf-8 -*-
"""
Created on Tue Jun 09 07:46:49 2015

@author: home
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:29:37 2015
Initial code purloined from the example at: https://unsupervisedlearning.wordpress.com/
@author: Brendan Neville

"""
import urllib
import imghdr
import os
import ConfigParser
import datetime
from pymongo import Connection
import time
from twython import Twython, TwythonRateLimitError, TwythonAuthError
 
config = ConfigParser.ConfigParser()
config.read('scraper.cfg')
 
# spin up twitter api
APP_KEY    = config.get('credentials','app_key')
APP_SECRET = config.get('credentials','app_secret')
OAUTH_TOKEN        = config.get('credentials','oath_token')
OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')

#twitter = Twython(app_key='Mfm5oNdGSPMvwhZcB8N4MlsL8',
#    app_secret='C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP',
#    oauth_token='3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G',
#    oauth_token_secret='HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO')
 
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()
 
# spin up database
DBNAME = config.get('database', 'name')

COLLECTION = config.get('database', 'collection')
print(DBNAME)
print(COLLECTION)

conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

print("twitter connection and database connection configured")


def print_tweets_date_period(start, end):
    results = tweets.find({'created_at': {'$gte': start, '$lt': end}})
    for doc in results:
        print str(doc['created_at']) + "\t" + doc['user']['screen_name'].encode('utf-8') +"\t"+ doc['text'].encode('utf-8').replace('\n', '')    
    print "Total_Printed = " + str(results.count())    
    

username = 'anasecretss'
username = 'needingbones'
#username = 'tiinyterry'

output = open("timeline-profiledes-data-" + username + ".txt","w")

# results = tweets.find({'user.screen_name': 'tiinyterry'})
results = tweets.find({'user.screen_name': username})
 
for tweet in results:
    output.write(tweet['user']['description'] + "\n")
    # print tweet['user']['description']

output.close()

print results.count()    
    
    