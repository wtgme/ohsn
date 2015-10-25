# -*- coding: utf-8 -*-
"""
Created on Fri Jun 05 09:00:50 2015
@author: home
"""
#import urllib
#import imghdr
#import os
#import ConfigParser
import pymongo
from twython import Twython, TwythonRateLimitError, TwythonAuthError
import datetime
import time
#import networkx as nx

# get these by registering an application with twitter
# Twitter application auth codes...    

# Twitter application auth codes...   
APP_KEY    = 'FUbZ6j65MskJ30wVTZVq3jzXZ'
APP_SECRET = 'qGi9QVdWkacsXbQrCC2hwOQBjsGjw2Sdaxi2UxvjEDAV3IQnxH'
OAUTH_TOKEN        = '3034707280-dMKiCKBZKvAmddJRDGos4B03yLIxlDkBdOVaONF'
OAUTH_TOKEN_SECRET = '2ICnWiz79ejyhrFk8wjW5bY0ovU7R3biw3okmXSOfpHON'

#Access Token	3034707280-dMKiCKBZKvAmddJRDGos4B03yLIxlDkBdOVaONF
#Access Token Secret	2ICnWiz79ejyhrFk8wjW5bY0ovU7R3biw3okmXSOfpHON
#Consumer Key (API Key)	FUbZ6j65MskJ30wVTZVq3jzXZ
#Consumer Secret (API Secret)	qGi9QVdWkacsXbQrCC2hwOQBjsGjw2Sdaxi2UxvjEDAV3IQnxH

# only get followers for poi with classification less than this:
# -1 is get no-one, 0 is the highest real classification.
# Not implemented yet...
FOLLOWER_POI_CLASSIFICATION_THRESHOLD = 1

# Futurework:
# if set to true we will get data for the follower nodes that we find...
# this is dangerous wrt the rate-limit and can explode rapidly.
# GET_FOLLOWER_NODE_DATA = False

# only check the follower/followee network at most every 1 weeks...
# we have data limits after-all
MIN_RESOLUTION = datetime.timedelta(seconds=1*604800)

# wait for ten minutes
IDLETIME = 60*10

# wait for 15 minutes if an exception occurs
ON_EXCEPTION_WAIT = 60*15

ERROR_LOG_FILENAME = 'log/TAPI_FollowerNetworkHarvester_ErrorLog_' + datetime.datetime.now() + '.log'
errorfile = open(ERROR_LOG_FILENAME, 'w')

# MongoDB database config and credentials
DBPOIURL = 'aicvm-bjn1c13-1.ecs.soton.ac.uk'
DBNAME_POI = 'echelon'
POI_COL = 'poi'

DBFOLLOWERURL = 'aicvm-bjn1c13-1.ecs.soton.ac.uk'
DBNAME_FOLLOWERS = 'echelon'
FOLLOWEREDGES_COL = 'edges'

# spin up database collections
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'

try:

    MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + DBPOIURL + '/' + DBNAME_POI
    connP = pymongo.MongoClient(MONGOAUTH)
    dbp = connP[DBNAME_POI]
    poi = dbp[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME_POI  + "." + POI_COL
    poi.create_index([("id", pymongo.DESCENDING)], unique=True)
    print "index created on " + POI_COL + " by id"            
    #---------------------------------------------
    
    MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + DBFOLLOWERURL + '/' + DBNAME_FOLLOWERS 
    connF = pymongo.MongoClient(MONGOAUTH)
    dbf = connF[DBNAME_FOLLOWERS]
    followeredges = dbf[FOLLOWEREDGES_COL]
    print  MONGOUSER +" connected to " + DBNAME_FOLLOWERS  + "." + FOLLOWEREDGES_COL
    followeredges.create_index([("id0", pymongo.ASCENDING), ("id1", pymongo.ASCENDING), ("relationship", pymongo.ASCENDING)])
    print "network unique index created on v0,v1,relationship"

except Exception:
    print MONGOUSER +" FAILED to connect to required databases"
    exit()

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()

print("twitter connection and database connection configured")

def handle_follower_rate_limiting():
    app_status = {'remaining':1} # prepopulating this to make the first 'if' check fail
    while True:
        wait = 0
        if app_status['remaining'] > 0:
            status = twitter.get_application_rate_limit_status(resources = ['followers', 'application'])
            app_status = status['resources']['application']['/application/rate_limit_status']
            home_status = status['resources']['followers']['/followers/ids']
            if home_status['remaining'] == 0:
                wait = max(home_status['reset'] - time.time(), 0) + 1 # addding 1 second pad
                time.sleep(wait)
            else:
                return
        else :
            wait = max(app_status['reset'] - time.time(), 0) + 10
            time.sleep(wait)

def handle_friend_rate_limiting():
    app_status = {'remaining':1} # prepopulating this to make the first 'if' check fail
    while True:
        wait = 0
        if app_status['remaining'] > 0:
            status = twitter.get_application_rate_limit_status(resources = ['friends', 'application'])
            app_status = status['resources']['application']['/application/rate_limit_status']
            home_status = status['resources']['friends']['/friends/ids']
            if home_status['remaining'] == 0:
                wait = max(home_status['reset'] - time.time(), 0) + 1 # addding 1 second pad
                time.sleep(wait)
            else:
                return
        else :
            wait = max(app_status['reset'] - time.time(), 0) + 10
            time.sleep(wait)
            
#def store_follower(follower, collection=nodes):
#    follower['created_at'] = datetime.datetime.strptime(follower['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
#    collection.insert(follower)


#def store_followers(followers, collection=nodes):
#     for follower in followers:
#         store_follower(follower)
  
#def getUserDetails(ids):
#    userDetails = []
#    if len(ids) > 100:
#        response = twitter.lookupUser(user_id = ','.join(str(a) for a in ids[0:99]))
#        userDetails += response
#        return getUserDetails(ids[100:]) + userDetails
#    else:
#        response = twitter.lookupUser(user_id = ','.join(str(a) for a in ids))
#        userDetails += response
#    return userDetails  
      
def getfollowersids(userid, maxfollowers=5000, edges=followeredges):
    next_cursor = -1
    while next_cursor != 0:   
        try:
            #if we need to do cursoring we do it here...
            #this is for cursoring, if we want to get more followers from each node than a single query will allow.    
            
            handle_follower_rate_limiting()
            #print("querying twitter")
            response = twitter.get_followers_ids(user_id=userid, count=maxfollowers, cursor = next_cursor)
            # store_followers(response['ids'])
            next_cursor = response['next_cursor']                
            
            for follower in response['ids']:
            # print follower['screen_name'] +"\t"+ follower['description'].encode('utf-8').replace('\n', ' ')
                edge = {}
                edge['id0'] = follower['id'] 
                # edge['screen_name_0'] = 
                edge['id1'] = userid
                # edge['screen_name_1'] = 
                edge['relationship'] = 'follower'
                # this is an observation we can merge observations into weighted and time period later.
                edge['last-date'] = datetime.datetime.now()
                edge['first-date'] = datetime.datetime.now()

                # N/A don;t have a status if its a follower lookup                    
                # a copy of the status that established it: this will contain all that is needed for export to NodeXL or otherwise.
                # edge['status'] = 
                try:
                    edges.insert(edge)
                except pymongo.errors.DuplicateKeyError:
                    edges.update({ 'id0': edge['id0'], 'id1': edge['id1'] , 'relationship': edge['relationship']}, {'$set':{'last-date':edge['last-date']}})

        except TwythonRateLimitError:
            #print "Rate-limit exception encountered. Sleeping for ~ 15 min before retrying"
            #print datetime.datetime.now().time()
            reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
            wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
            time.sleep(wait)
            # try again
        except TwythonAuthError, e:
            # most likely this is due to a private user, so its best to give up.
            poi.update({'id':userid},{'$set':{"follower_auth_error_flag": True}}, upsert=False)
            next_cursor=0
            #print e
        except Exception, e:        
            error = "ERROR\t getfollowersids(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
            print error            
            errorfile.write(error)
            errorfile.flush()
            time.sleep(ON_EXCEPTION_WAIT)
            pass

    #print "Ran out of followers for the current userid - setting last scrape time and AuthError = False"
    poi.update({'id':userid},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':False}}, upsert=False)

def getfriendsids(userid, maxfollowers=5000, edges=followeredges):
    next_cursor = -1
    while next_cursor != 0:   
        try:
            #if we need to do cursoring we do it here...
            #this is for cursoring, if we want to get more followers from each node than a single query will allow.    
            
            handle_friend_rate_limiting()
            #print("querying twitter")
            response = twitter.get_friends_ids(user_id=userid, count=maxfollowers, cursor = next_cursor)
            # store_followers(response['ids'])
            next_cursor = response['next_cursor']                
            
            for follower in response['ids']:
            # print follower['screen_name'] +"\t"+ follower['description'].encode('utf-8').replace('\n', ' ')
                edge = {}
                edge['id0'] = userid
                # edge['screen_name_0'] = 
                edge['id1'] = follower['id'] 
                # edge['screen_name_1'] = 
                edge['relationship'] = 'friend'
                # this is an observation we can merge observations into weighted and time period later.
                edge['last-date'] = datetime.datetime.now()
                edge['first-date'] = datetime.datetime.now()

                # N/A don;t have a status if its a follower lookup                    
                # a copy of the status that established it: this will contain all that is needed for export to NodeXL or otherwise.
                # edge['status'] = 
                try:
                    edges.insert(edge)
                except pymongo.errors.DuplicateKeyError:
                    edges.update({ 'id0': edge['id0'], 'id1': edge['id1'] , 'relationship': edge['relationship']}, {'$set':{'last-date':edge['last-date']}})

        except TwythonRateLimitError:
            #print "Rate-limit exception encountered. Sleeping for ~ 15 min before retrying"
            #print datetime.datetime.now().time()
            reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
            wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
            time.sleep(wait)
            # try again
        except TwythonAuthError, e:
            # most likely this is due to a private user, so its best to give up.
            # poi.update({'id':userid},{'$set':{"follower_auth_error_flag": True}}, upsert=False)
            poi.update({'id':userid},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':True}}, upsert=False)

            next_cursor=0
            #print e
        except Exception, e:        
            error = "ERROR\t getfriendsids(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
            print error            
            errorfile.write(error)
            errorfile.flush()
            time.sleep(ON_EXCEPTION_WAIT)
            pass

    #print "Ran out of friends for the current userid - setting last scrape time and AuthError = False"
    poi.update({'id':userid},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':False}}, upsert=False)


#def getfollowersidsrecursive(userid, hop=0, maxhop=2, maxfollowers=5000, nodes=nodes, edges=followeredges):
#    
#    hop = hop + 1
#    if hop <= maxhop:
#        
#        next_cursor = -1
#        while next_cursor != 0:   
#            try:
#                #if we need to do cursoring we do it here...
#                #this is for cursoring, if we want to get more followers from each node than a single query will allow.    
#                
#                handle_rate_limiting()
#                print("querying twitter")
#                response = twitter.get_followers_ids(user_id=userid, count=maxfollowers, cursor = next_cursor)
#                # store_followers(response['ids'])
#                next_cursor = response['next_cursor']                
#                
#                for follower in response['ids']:
#                # print follower['screen_name'] +"\t"+ follower['description'].encode('utf-8').replace('\n', ' ')
#                    edge = {}
#                    edge['id0'] = follower['id'] 
#                    # edge['screen_name_0'] = 
#                    edge['id1'] = userid
#                    # edge['screen_name_1'] = 
#                    edge['relationship'] = 'follower'
#                    # this is an observation we can merge observations into weighted and time period later.
#                    edge['date'] = datetime.datetime.now()
#
#                    # N/A don;t have a status if its a follower lookup                    
#                    # a copy of the status that established it: this will contain all that is needed for export to NodeXL or otherwise.
#                    # edge['status'] = 
#                    collection.insert(edge)
#
#                    getfollowersids(follower, hop, maxhop, maxfollowers, nodes, edges)
#
#            except TwythonRateLimitError:
#                print "Rate-limit exception encountered. Sleeping for ~ 15 min before retrying"
#                print datetime.datetime.now().time()
#                reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
#                wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
#                time.sleep(wait)
#                # try again
#            except TwythonAuthError, e:
#                # most likely this is due to a private user, so its best to give up.
#                next_cursor=0
#                print e
#            except Exception, e:
#                print e
#                print datetime.datetime.now().time()
#                time.sleep(30)
#            # print "Non rate-limit exception encountered. Sleeping for 15 min before retrying"
#            # time.sleep(60*15)

def get_poi_followers():
     
        while True:
            # selects on the basis of choosing the one that hasn't been updated in a long time.            
            # don't waste time/twitter calls checking if it hasn't been long enough
            try:
                nextpoi = poi.find({'poi_classification': { '$lt': FOLLOWER_POI_CLASSIFICATION_THRESHOLD}, 'follower_auth_error_flag':False}, sort=[('datetime_last_follower_scrape',1)]).limit(1)[0]     
                #print("next person of interest = " + nextpoi['id'] + "\t" + nextpoi['screen_name'])                
                next_harvest_due_at = nextpoi['datetime_last_follower_scrape'] +  MIN_RESOLUTION
                if next_harvest_due_at > datetime.datetime.now():
                    print "no user due to be scraped"
                    # it wont wait till this poi is due to check again, as new poi might be added to the db before that.
                    # set this to about ten minutes.
                    time.sleep(IDLETIME)
                else:
                    # Do both friends and followers....
                    print nextpoi['id']
                    getfollowersids(nextpoi['id'])
                    getfriendsids(nextpoi['id'])
                    
            except Exception, e:
                error = "ERROR" + "\t" + "get_poi_followers()\t" + str(e.__class__) +"\t"+ str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
                errorfile.write(error)
                errorfile.flush()
                time.sleep(ON_EXCEPTION_WAIT)
                pass
            
        
        
get_poi_followers()        
        
#while True:
#    nextpoi = poi.find{poi_classification < FOLLOWER_POI_CLASSIFICATION_THRESHOLD} sort by datetime_last_follower_scrape ASC limit 1
#    
#    if datetime.datetime.now() - nextpoi['datetime_last_follower_scrape'] > MIN_RESOLUTION:
#        auth_error = scape(nextpoi['id'])
#        if auth_error:
#            update poi db with follower_auth_error
#        
#        
#        # update poi_db with datetime_last_follower_scrape = datetime.datetime.now() and no autherror
#        poi.update({'id':user_id},{'$set':{"datetime_last_follower_scrape": datetime.datetime.now(), 'follower_auth_error_flag':False}}, upsert=False)
#                 
#    else:    
#        time_next_scrape = datetime_last_follower_scrape + MIN_RESOLUTION
#        time.wait(time_next_scrape)




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

# @b00bsnation

#followers = twitter.get_followers_list(screen_name='ementzakis', count=10)
#store_followers(followers)

# getuserdata.
#
#getfollowersids(591266520)
#
#print "...COMPLETE..."
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
