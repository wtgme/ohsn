# -*- coding: utf-8 -*-
"""
Created on Fri Jun 05 09:00:50 2015

@author: home
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

#params = {'id':606043007612293120}
##params = {'count':200, 'contributor_details':True, 'since_id':latest}
#            
#retweets = twitter.get_retweets(**params)
#for retweeter in retweets:
#    print retweeter
#
#retweeters = twitter.get_retweeters_ids(**params)

#.get_user_timeline(**params)

edges = {}
nodes = {}

def getfollowers(name, nodes=nodes, edges=edges):
    next_cursor = -1
    followers = timeline_twitter.get_followers_list(screen_name=name, count=200)

    for follower in followers['users']:
        print follower['screen_name'] +"\t"+ follower['description'].encode('utf-8').replace('\n', ' ')

        if node is not in db:

        followernode = {}
        followernode['screen_name'] = follower['screen_name']
        followernode['description'] = follower['description'].encode('utf-8').replace('\n', ' ')
        
        edge = {}
        edge['v0'] = screen_name
        edge['v1'] = follower['screen_name']
        getfollowers(name)


for follower in followers['users']:
    fh1 = fh1.update(timeline_twitter.get_followers_list(screen_name=follower['screen_name'], count=200))

    

