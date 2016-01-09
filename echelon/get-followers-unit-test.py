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
import datetime
import networkx as nx
 
config = ConfigParser.ConfigParser()
config.read('scraper.cfg')
 
# spin up twitter api
APP_KEY    = config.get('credentials','app_key')
APP_SECRET = config.get('credentials','app_secret')
OAUTH_TOKEN        = config.get('credentials','oath_token')
OAUTH_TOKEN_SECRET = config.get('credentials','oath_token_secret')


DBNAME = 'twitter_test'
COLLECTION = 'testfolloweredgescursored'
NODECOLLECTION = 'testfollowernodescursored'


#print(DBNAME)
#print(COLLECTION)
#print(NODECOLLECTION)
#print(FOLLOWERCOLLECTION)

conn = Connection()
db = conn[DBNAME]
edges = db[COLLECTION]
nodes = db[NODECOLLECTION]

#twitter = Twython(app_key='Mfm5oNdGSPMvwhZcB8N4MlsL8',
#    app_secret='C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP',
#    oauth_token='3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G',
#    oauth_token_secret='HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO')
 
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()

#params = {'id':606043007612293120}
##params = {'count':200, 'contributor_details':True, 'since_id':latest}
#            
#retweets = twitter.get_retweets(**params)
#for retweeter in retweets:
#    print retweeter
#
#retweeters = twitter.get_retweeters_ids(**params)

#edges = []
#nodes = dict()

def handle_rate_limiting():
    app_status = {'remaining':1} # prepopulating this to make the first 'if' check fail
    while True:
        wait = 0
        if app_status['remaining'] > 0:
            status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
            app_status = status['resources']['application']['/application/rate_limit_status']
            home_status = status['resources']['statuses']['/statuses/home_timeline']
            if home_status['remaining'] == 0:
                wait = max(home_status['reset'] - time.time(), 0) + 1 # addding 1 second pad
                time.sleep(wait)
            else:
                return
        else :
            wait = max(app_status['reset'] - time.time(), 0) + 10
            time.sleep(wait)
            
            
def store_follower(follower, collection=nodes):
    follower['created_at'] = datetime.datetime.strptime(follower['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    collection.insert(follower)
  
def store_edge(edge, collection=edges):
    # print "todo: can we get the edge creation date????"
    collection.insert(edge)

def store_followers(followers, collection=nodes):
     for follower in followers:
         store_follower(follower)
  
def getUserDetails(ids):
    userDetails = []
    if len(ids) > 100:
        response = twitter.lookupUser(user_id = ','.join(str(a) for a in ids[0:99]))
        userDetails += response
        return getUserDetails(ids[100:]) + userDetails
    else:
        response = twitter.lookupUser(user_id = ','.join(str(a) for a in ids))
        userDetails += response
    return userDetails  
  
  
def getfollowers(name, hop=0, maxhop=1, maxfollowers=200, nodes=nodes, edges=edges):
    
    hop = hop + 1
    if hop <= maxhop:
        
        next_cursor = -1
        while next_cursor != 0:   
            try:
                #if we need to do cursoring we do it here...
                #this is for cursoring, if we want to get more followers from each node than a single query will allow.    
                
                handle_rate_limiting()
                print("querying twitter")
                response = twitter.get_followers_list(screen_name=name, count=maxfollowers, cursor = next_cursor)
                store_followers(response['users'])
                next_cursor = response['next_cursor']                
                
                for follower in response['users']:
                # print echelon['screen_name'] +"\t"+ echelon['description'].encode('utf-8').replace('\n', ' ')
                    edge = {}
                    edge['v0'] = follower['screen_name']
                    edge['v1'] = name
                    store_edge(edge)
                    getfollowers(follower['screen_name'], hop, maxhop, maxfollowers, nodes, edges)

            except TwythonRateLimitError:
                print "Rate-limit exception encountered. Sleeping for ~ 15 min before retrying"
                print datetime.datetime.now().time()
                reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
                wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
                time.sleep(wait)
                # try again
            except Exception, e:
                print e
            # print "Non rate-limit exception encountered. Sleeping for 15 min before retrying"
            # time.sleep(60*15)
               
# @b00bsnation

#followers = twitter.get_followers_list(screen_name='ementzakis', count=10)
#store_followers(followers)

# getuserdata.

getfollowers('ementzakis')

#Twitter API returned a 401 (Unauthorized), An error occurred processing your request.
#Non rate-limit exception encountered. Sleeping for 15 min before retrying

#for edge in edges:
#    print edge['v0'] + "\t" + edge['v1']
#
#print "Node Count :" + str(len(nodes))
#print "Edge Count :" + str(edges.count())