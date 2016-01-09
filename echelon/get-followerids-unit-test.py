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
from twython import Twython, TwythonRateLimitError, TwythonAuthError
import datetime
import networkx as nx
    
# MongoDB database config and credentials
DBLOGIN = 'bjn1c13'
DBPASSWD = ''

DBPOIURL = 'aicvm-bjn1c13-1'
DBFOLLOWERURL = aicvm-bjn1c13-2
DBNAME_POI = 'node1'
DBNAME_FOLLOWERS = 'node2'

FOLLOWERNETWORK_COL = 'follower_edge_network'
POI_COL = 'poi_col'
 
# get these by registering an application with twitter
# Twitter application auth codes...    
APP_KEY    = 'Junk'
APP_SECRET = 'Junk'
OAUTH_TOKEN        = 'Junk'
OAUTH_TOKEN_SECRET = 'Junk'

# only get followers for poi with classification less than this:
# -1 is get no-one, 0 is the highest real classification.
# Not implemented yet...
FOLLOWER_POI_CLASSIFICATION_THRESHOLD = -1

# only check the echelon/followee network at most every 1 weeks...
# we have data limits after-all
MIN_RESOLUTION = timedelta(1*604800)

ERROR_LOG_FILENAME = 'TAPI_FollowerNetworkHarvester_ErrorLog_' + datetime.datetime.now() + '.log'

"""
    Psuedocode    
"""

# spin up database collections

# Choose a connection method:
# for local use this: 
conn_poi = pymongo.MongoClient()
conn_followers = pymongo.MongoClient()
# for remote use this:
# conn_poi = MongoClient(DBPOIURL)
# conn_followers = MongoClient(DBFOLLOWERURL)

db = conn_poi[DBNAME_POI]
db = conn_followers[DBNAME_FOLLOWERS]

poi = db[POI_COL]
followeredges = db[FOLLOWERNETWORK_COL]

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()

print("twitter connection and database connection configured")


edge['id0'] = 
edge['screen_name_0'] = 
edge['id1'] = 
edge['screen_name_1'] = 
edge['relationship'] = 
# this is an observation we can merge observations into weighted and time period later.
edge['date'] = 
# a copy of the status that established it: this will contain all that is needed for export to NodeXL or otherwise.
edge['status'] = 

upload...
update poi ...
 
while True:

    nextpoi = poi.find{poi_classification < FOLLOWER_POI_CLASSIFICATION_THRESHOLD} sort by datetime_last_follower_scrape ASC limit 1
    if datetime.datetime.now() - nextpoi['datetime_last_follower_scrape'] > MIN_RESOLUTION:
        auth_error = scape(nextpoi['id'])
        if auth_error:
            update poi db with follower_auth_error
            
        update poi_db with datetime_last_follower_scrape = datetime.datetime.now()
            
    else:    
        time_next_scrape = datetime_last_follower_scrape + MIN_RESOLUTION
        time.wait(time_next_scrape)



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
  
  
def getfollowersids(userid, hop=0, maxhop=2, maxfollowers=5000, nodes=nodes, edges=edges):
    
    hop = hop + 1
    if hop <= maxhop:
        
        next_cursor = -1
        while next_cursor != 0:   
            try:
                #if we need to do cursoring we do it here...
                #this is for cursoring, if we want to get more followers from each node than a single query will allow.    
                
                handle_rate_limiting()
                print("querying twitter")
                response = twitter.get_followers_ids(user_id=userid, count=maxfollowers, cursor = next_cursor)
                # store_followers(response['ids'])
                next_cursor = response['next_cursor']                
                
                for follower in response['ids']:
                # print echelon['screen_name'] +"\t"+ echelon['description'].encode('utf-8').replace('\n', ' ')
                    edge = {}
                    edge['v0'] = follower
                    edge['v1'] = userid
                    store_edge(edge)
                    getfollowersids(follower, hop, maxhop, maxfollowers, nodes, edges)

            except TwythonRateLimitError:
                print "Rate-limit exception encountered. Sleeping for ~ 15 min before retrying"
                print datetime.datetime.now().time()
                reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
                wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
                time.sleep(wait)
                # try again
            except TwythonAuthError, e:
                # most likely this is due to a private user, so its best to give up.
                next_cursor=0
                print e
            except Exception, e:
                print e
                print datetime.datetime.now().time()
                time.sleep(30)
            # print "Non rate-limit exception encountered. Sleeping for 15 min before retrying"
            # time.sleep(60*15)
               
# @b00bsnation

#followers = twitter.get_followers_list(screen_name='ementzakis', count=10)
#store_followers(followers)

# getuserdata.

getfollowersids(591266520)

print "...COMPLETE..."
#response = twitter.get_followers_ids(user_id=591266520)
#
#print response
#
#for item in response:
#    print item

#Twitter API returned a 401 (Unauthorized), An error occurred processing your request.
#Non rate-limit exception encountered. Sleeping for 15 min before retrying

#for edge in edges:
#    print edge['v0'] + "\t" + edge['v1']
#
#print "Node Count :" + str(len(nodes))
#print "Edge Count :" + str(edges.count())