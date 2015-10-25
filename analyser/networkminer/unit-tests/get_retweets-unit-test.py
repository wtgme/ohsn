# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 10:00:01 2015

@author: home
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
#DBNAME = config.get('database', 'name')
#COLLECTION = config.get('database', 'collection')
#COLLECTION = 'manostimeline'
#print(DBNAME)
#print(COLLECTION)
#
#conn = Connection()
#db = conn[DBNAME]
#tweets = db[COLLECTION]

print("twitter connection and database connection configured")

orig_tweet_id = 608648346048303104
manos_tweet_id = 608658245352353792



"""
Returns fully-hydrated tweet objects 
for up to 100 tweets per request, as 
specified by comma-separated values 
passed to the id parameter.
Requests / 15-min window (user auth) 180
Requests / 15-min window (app auth) 60
"""
params = {'id':orig_tweet_id}
response = twitter.lookup_status(**params)
#print response
for status in response:
    print status['user']['screen_name'] 
    print status['retweet_count']

"""
Returns a collection of up to 100 user IDs belonging 
to users who have retweeted the tweet specified by the 
id parameter.

you can cursor this...

Requests / 15-min window (user auth) 15
Requests / 15-min window (app auth) 60

"""
params = {'count':100, 'id':orig_tweet_id, 'cursor':-1}

response = twitter.get_retweeters_ids(**params)
#response['previous_cursor']
#response['previous_cursor_str']
print response['next_cursor']
#response['next_cursor_str']
for retweeter_id in response['ids']:
    print retweeter_id

"""
Returns a collection of the 100 most 
recent retweets of the tweet specified by the id parameter.

Requests / 15-min window (user auth) 15
Requests / 15-min window (app auth) 60

you CANNOT cursor this...

"""
params = {'count':100, 'id':orig_tweet_id}
response= twitter.get_retweets(**params)
# print response
for item in response:
    print item['user']['screen_name']






