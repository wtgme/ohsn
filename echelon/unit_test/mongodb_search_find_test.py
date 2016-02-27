# -*- coding: utf-8 -*-
"""
Created on Mon Jun 01 12:14:24 2015

@author: home
"""

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

print("loading list of nodes of interest...")

#Get all the usernames 

usernames = {'needingbones', 'anasecretss'}

# Query a username till you get the no-more tweets message, then move onto the next, eventually wrap around and start over again.

while True:
    # Get all the usernames from the nodes database
    for username in usernames:
        print username
        # get the user's timeline or in all likelihood the update to their timeline
        # process those tweets for new mentions/replies 
        # if those users are new.. add those users to the list of nodes to get timelines for... mark these nodes with the orginal usernames rank + 1...
        # if the user is already in the database check if thier rank is currently >= thisuserrank + 1 if so reduce their rank to thisuserrank + 1
        
        

try:
    # last_tweet = tweets.find(None, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
    last_tweet = tweets.find({'user.screen_name':username}, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
    if last_tweet:
        latest = last_tweet['id']
        print str(latest)
except Exception, e:
    print "Error retrieving tweets. username not found or database probably needs to be populated before it can be queried." + str(e)
 
 