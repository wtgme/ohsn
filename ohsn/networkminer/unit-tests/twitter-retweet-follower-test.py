# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:29:37 2015
Initial code purloined from the example at: https://unsupervisedlearning.wordpress.com/

The aim of this test fragment is to see if we can get a meaningful network of retweets...

@author: Brendan Neville

"""
import urllib
import imghdr
import os
import ConfigParser
import datetime
from pymongo import Connection
import time
from twython import Twython, TwythonRateLimitError
 
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
 
timeline_twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
timeline_twitter.verify_credentials()
 
# spin up database
DBNAME = config.get('database', 'name')

COLLECTION = config.get('database', 'collection')
print(DBNAME)
print(COLLECTION)

conn = Connection()
db = conn[DBNAME]
tweets = db[COLLECTION]

print("twitter connection and database connection configured")

#def get_retweets(tweetid):
#    # params = {'id':tweetid, 'count':100}
#    results = twitter.get_retweets(id=tweetid)
#    for result in results:
#        print result
    



# Get all the usernames 
# Get all the usernames from the nodes database
print("loading list of nodes of interest...")
print "TODO: Change so it runs through and monitors the users in the node database with rank <= 2..."
print "TODO: alter the schema of the tweet to match the edge network spec from the network miner..."
print "TODO: make the tweet id a unique index to avoid duplicates... db.collection.createIndex( { a: 1 }, { unique: true } )"

#note retweets can't be retweeted...

#who gives a shit about more than 100....

#same goes for followers...

usernames = {'needingbones', 'anasecretss', 'tiinyterry'}
# get_user_timelines(usernames, persistant=False)

try:
    
    # Fix this....
    # why aien;t it returning tweets that our ed's have had retweeted?
    
    tweeties = tweets.find(None, sort=[('retweet_count',-1)])
    for tweet in tweeties:
        if tweet['retweeted_status']['id'] is None:
            
            print tweet['id']
            print tweet['retweet_count']
            print ""
            # tweetid = 605455779580289026
            # tweetid = "595218763743666177"
            # tweetid = 595178774209101824
            params = {'id':tweet['id'], 'count':100}
            results = timeline_twitter.get_retweets(**params)
            for result in results:
                print result['id']
        print "end of results"
            
except TwythonRateLimitError, e:
    print "Rate-limit exception encountered. Sleeping for ~ 15 min before retrying"
    reset = int(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
    wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
    time.sleep(wait)
except Exception, e:
    print e
    print "Non rate-limit exception encountered. Sleeping for 15 min before retrying"
    time.sleep(60*15)