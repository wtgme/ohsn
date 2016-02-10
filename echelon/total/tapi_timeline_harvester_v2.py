# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:29:37 2015
Initial code purloined from the example at: https://unsupervisedlearning.wordpress.com/
@author: Brendan Neville

"""
 
import urllib
import imghdr
import os
import datetime
import pymongo
import time
from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
import re

# spin up database collections
# Echelon connection    

MONGOURL = 'aicvm-bjn1c13-1.ecs.soton.ac.uk'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'
TIMELINES_COL = 'timelines'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    
    poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
    poi.create_index([("id", pymongo.DESCENDING)], unique=True)
    print "index created on " + POI_COL + " by id"            

    timelines = db[TIMELINES_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + TIMELINES_COL
    timelines.create_index([("id", pymongo.DESCENDING)], unique=True)
    print "timeline unique index created on tweet id"

except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()

# Twitter application auth codes...    
APP_KEY    = 'Mfm5oNdGSPMvwhZcB8N4MlsL8'
APP_SECRET = 'C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP'
OAUTH_TOKEN        = '3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
OAUTH_TOKEN_SECRET = 'HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO'

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()
 
ON_EXCEPTION_WAIT = 60*16

print("twitter connection and database connection configured")

rate_limit_status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])

def store_tweets(tweets_to_save, collection=timelines):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    for tw in tweets_to_save:
        tw['created_at'] = datetime.datetime.strptime(tw['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        tw['user']['created_at'] = datetime.datetime.strptime(tw['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        # get pictures in tweet...
 
    collection.insert(tweets_to_save)
    print("storing tweets")
 
def handle_rate_limiting():
    global rate_limit_status
    print "handling rate limiting:"
    
    Its in the fucking function headers!!!!!
    
    # this is why we called handle rate limiting right!
    rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'] = 0
    
    # this is what I'm waiting for right !!!
    while rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'] == 0:
        
        if rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining'] > 0:
                try:                                
                    rate_limit_status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])

                    if rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'] == 0:
                        wait = max(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'] - time.time(), 0) + 5 # addding 1 second pad
                        print "/statuses/user_timeline remaining == 0; waiting" + str(wait) + "seconds"
                        time.sleep(wait)
                    else:
                        return
                    
                except TwythonRateLimitError:
                    reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
                    wait = max(reset - time.time(), 0) + 60 # addding 10 second pad
                    print "Rate-limit exception encountered getting rate_limit_status. Retry in " + str(wait) + " seconds"
                    print datetime.datetime.now().time()                    
                    time.sleep(wait)
                except Exception:
                    print "twitter.get_application_rate_limit_status() threw Exception, waiting..." + str(ON_EXCEPTION_WAIT) + " seconds"
                    time.sleep(ON_EXCEPTION_WAIT)
    
        else :
            # if we ran out of rate limit calls assume if we wait they will reset it
            wait = max(rate_limit_status['resources']['application']['/application/rate_limit_status']['reset'] - time.time(), 0) + 10
            print "out of rate_limit_calls waiting for reset in " + str(wait) + " seconds"            
            time.sleep(wait)
            # add one so it will go round and make the call we can but assume twitter has reset...
            rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining'] += 1
        
def get_user_timeline(username):
    print username
    # get the user's timeline or in all likelihood the update to their timeline
    # process those tweets for new mentions/replies 
    # if those users are new.. add those users to the list of nodes to get timelines for... mark these nodes with the orginal usernames rank + 1...
    # if the user is already in the database check if thier rank is currently >= thisuserrank + 1 if so reduce their rank to thisuserrank + 1
    latest = None   # most recent id scraped
    #print "TODO: Change this so it gets the last tweet of a specific user..."
       
    try:
        # last_tweet = tweets.find(None, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
        last_tweet = timelines.find({'user.screen_name':username}, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
        if last_tweet:
            latest = last_tweet['id']
            print str(latest)
    except Exception, e:
        print "Error retrieving tweets. username not found or database probably needs to be populated before it can be queried." + str(e)
    
    while True:
        try:
            newest = None # this is just a flag to let us know if we should update the "latest" value
            #params = {'screen_name':'anasecretss', 'since_id':latest}
            print "latest = " + str(latest)
            # latest = 0
            params = {'count':200, 'contributor_details':True, 'screen_name':username, 'since_id':latest, 'include_rts':1}
            #params = {'count':200, 'contributor_details':True, 'since_id':latest}
            
            handle_rate_limiting()
            #home = twitter.get_home_timeline(**params)
            home = twitter.get_user_timeline(**params)
            print("querying twitter")
            if home:
                while home:
                    store_tweets(home)
     
                    # Only update "latest" if we're inside the first pass through the inner while loop
                    if newest is None:
                        newest = True
                        latest = home[0]['id']
     
                    params['max_id'] = home[-1]['id'] - 1
                    handle_rate_limiting()
                    home = twitter.get_user_timeline(**params)
                    # user_timeline=twitter.getUserTimeline(screen_name="dksbhj", count=200, include_rts=1)
            else:
                print "Ran out of tweets for the current username"
                break
     
        except TwythonRateLimitError, e:
            print "Rate-limit exception encountered. Sleeping for ~ 15 min before retrying"
            print datetime.datetime.now().time()
            reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
            wait = max(reset - time.time(), 0) + 15  # addding 15 second pad
            time.sleep(wait)
        except TwythonAuthError, e:

        except TwythonError, e:
        pattern = re.compile('\s+404\s+', re.IGNORECASE)
        match = pattern.search(str(e))
        if match:
            poi.update({'id':user_id},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
            home = None
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_timeline(" + str(user_id) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_404_WAIT) + " before retrying\n" 
            print error            
            errorfile.write(error)
            errorfile.flush()
        else:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_timeline(" + str(user_id) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
            print error            
            errorfile.write(error)
            errorfile.flush()

        pass  
        
        print datetime.datetime.now().time()
        reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
        wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
        time.sleep(wait)
                          
            # most likely this is due to a private user, so its best to give up.
            home = None
            print e
            break
        except Exception, e:
            print e
            print "Non rate-limit exception encountered. Sleeping for 15 min before retrying"
            time.sleep(ON_EXCEPTION_WAIT)
    
    
def get_user_timelines(usernames, persistant=False):

    if persistant:       
        while True:
            for username in usernames:
                get_user_timeline(username)
       
            print "Checked for updates on all the usernames... going around again... in 1 minute"
            # time.sleep(60*15)
            time.sleep(60*1)
    else:
        for username in usernames:
            get_user_timeline(username)

# Get all the usernames 
# Get all the usernames from the nodes database
print("loading list of nodes of interest...")
print "TODO: Change so it runs through and monitors the users in the node database with rank <= 2..."

usernames = {'needingbones', 'anasecretss', 'tiinyterry'}
# usernames = {'ementzakis'}
get_user_timelines(usernames, persistant=True)

#username = 'drbnev'
#get_user_timeline(username)
