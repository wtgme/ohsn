# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:29:37 2015

Initial code purloined from the example at: https://unsupervisedlearning.wordpress.com/
Since then I've changed quite a bit, but credit where its due :)

@author: Brendan Neville

"""
#import urllib
#import imghdr
#import os
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

TIMELINE_POI_CLASS_THRESHOLD = 1

# GET_TIMELINE_IMAGES = False
#current TAPI max is 200
GET_USER_TIMELINE_COUNT = 200
# wait for 15 minutes if an exception occurs
ON_EXCEPTION_WAIT = 60*15

# ON_404_WAIT = 45
# don't scrape a user more than once every day.
# Turn this into a timedelta
MIN_RESOLUTION = datetime.timedelta(seconds=86400)
# if no poi are due to be harvested wait this long..
# the logic being that if you dynamically add new poi it will spot the new poi in this amount of time and harvest it
IDLETIME = 60*10 # 10 minutes
# if a non-rate-limit or authorisation error occurs log it here....    
#ERROR_LOG_FILENAME = 'log/TAPI_TimelineHarvester_ErrorLog_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.log'
#errorfile = open(ERROR_LOG_FILENAME, 'w')

timeline_twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
timeline_twitter.verify_credentials()

try:
    rate_limit_status  = timeline_twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
except:
    print "Exception occured getting rate-limit-status sleeping till it MIGHT clear then exiting"
    reset = int(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
    wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
    exit()

#handle_rate_limiting
#
#timeline_calls_left = 0
#timeline_call_reset = 
#follower_calls_left = 0
#follower_call_reset =
#friends_calls_left = 0
#friends_call_reset =
#
#run until the thing your querying goes to zero and then return giving the others a chance to go when they are all zero
#wait for a reset.
#
#this way we don't hammer the rate-limit endpoint and we don;t wait if we have calls left on any endpoint.
 
#def get_pictures(tweet):
#        # Get pictures in the tweets store as date-tweet-id-username.ext
#        try:
#            for item in tweet['entities']['media']:
#                # print item['media_url_https']
#                if item['type']=='photo':
#                    # print "PHOTO!!!"
#                    urllib.urlretrieve(item['media_url_https'], 'api-timelines-scraper-media/' + item['id_str'])
#                    # code to get the extension.... 
#                    ext = imghdr.what('api-timelines-scraper-media/' + item['id_str'])
#                    os.rename('api-timelines-scraper-media/' + item['id_str'], 'api-timelines-scraper-media/' + item['id_str'] + "." + ext)
#        except Exception:
#            #error = "ERROR" + "\t" + "get_pictures()\t" + str(e.__class__) +"\t"+ str(e) 
#            #errorfile.write(error)
#            #errorfile.flush()
#            pass

def store_tweets(tweets_to_save, collection=timelines):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    for tw in tweets_to_save:
        tw['created_at'] = datetime.datetime.strptime(tw['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        tw['user']['created_at'] = datetime.datetime.strptime(tw['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        # get pictures in tweet...
#        if GET_TIMELINE_IMAGES:
#            get_pictures(tw)
 
    collection.insert(tweets_to_save)
    print("storing tweets")




#def handle_rate_limiting():
#    app_status = {'remaining':1} # prepopulating this to make the first 'if' check fail
#    # global rate_limit_status
#    
#    while True:
#        wait = 0
#        # if rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining'] > 0:
#        if app_status['remaining'] > 0:
#            try:
#                # This will crash if both app_staus remaining and home_status remaining are 0                
#                # rate_limit_status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
#                status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
#                app_status = status['resources']['application']['/application/rate_limit_status']
#                home_status = status['resources']['statuses']['/statuses/user_timeline']
#                if home_status['remaining'] == 0:
#                    print "home_status == 0; waiting for reset"    
#                    wait = max(home_status['reset'] - time.time(), 0) + 5 # addding 1 second pad
#                    time.sleep(wait)
#                else:
#                    return
#            except TwythonRateLimitError, e:
#                reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
#                wait = max(reset - time.time(), 0) + 10 # addding 10 second pad                
#                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONRATEERROR\t handle_rate_limiting()" + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(wait) + " before retrying\n" 
#                print error     
#                print "Rate-limit exception encountered. Sleeping for before retrying"
#                print datetime.datetime.now().time()
#                time.sleep(wait)
#            except TwythonError, e:
#                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t handle_rate_limiting()" + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
#                print error            
##                errorfile.write(error)
##                errorfile.flush()
#                time.sleep(ON_EXCEPTION_WAIT)
#                
#        else :
#            # wait = max(rate_limit_status['resources']['application']['/application/rate_limit_status']['reset'] - time.time(), 0) + 10            
#            wait = max(app_status['reset'] - time.time(), 0) + 10
#            print "app_status == 0; waiting for reset"            
#            time.sleep(wait)
#            app_status['remaining'] += 1 
#            # rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining'] += 1


def handle_rate_limiting():
    
    if rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining'] == 0:
            print "last function call reset in " + str(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
            print "last function call reset in " + str(timeline_twitter.get_lastfunction_header('x-rate-limit-remaining'))
            print "rate-limit-status call reset in " + str(rate_limit_status['resources']['application']['/application/rate_limit_status']['reset'])
            reset = rate_limit_status['resources']['application']['/application/rate_limit_status']['reset']
            # reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
            print "waiting " +str(reset) + "seconds"            
            wait = max(reset - time.time(), 0) + 10 # addding 10 second pad                
            time.sleep(wait)

    home_status_remaining = 0
    
    while home_status_remaining == 0:
        wait = 0
        print "in handle_rate-limit loop" 
        try:                
            # rate_limit_status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
            status = timeline_twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
            print "rate-limit-status call reset in " + str(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
            print "rate-limit-status call reset in " + str(timeline_twitter.get_lastfunction_header('x-rate-limit-remaining'))
            app_status = status['resources']['application']['/application/rate_limit_status']

            home_status = status['resources']['statuses']['/statuses/user_timeline']
            if home_status['remaining'] == 0:
                home_status_remaining = 0
                print "home_status == 0; waiting for reset"    
                wait = max(home_status['reset'] - time.time(), 0) + 5 # addding 1 second pad
                time.sleep(wait)
            else:
                return
        
        except TwythonRateLimitError, e:
            print "rate-limit-status call reset in " + str(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
            print "rate-limit-status call reset in " + str(timeline_twitter.get_lastfunction_header('x-rate-limit-remaining'))
            reset = int(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
            wait = max(reset - time.time(), 0) + 10 # addding 10 second pad                
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONRATEERROR\t handle_rate_limiting()" + ")\t" + str(e.__class__) +"\t" + str(e) + "  Sleeping for " + str(wait) + " before retrying\n" 
            print error     
            print "Rate-limit exception encountered. Sleeping before retrying"
            print datetime.datetime.now().time()
            time.sleep(wait)
            app_status = {'remaining':1}
            # wait = max(rate_limit_status['resources']['application']['/application/rate_limit_status']['reset'] - time.time(), 0) + 10            
#            print "app_status['reset'] = " + str(app_status['reset'])
#            wait = max(app_status['reset'] - time.time(), 0) + 10
#            print "app_status == 0; waiting for reset"            
#            time.sleep(wait)
#            app_status['remaining'] += 1 
            # rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining'] += 1

        except TwythonError, e:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t handle_rate_limiting()" + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
            print error            
#                errorfile.write(error)
#                errorfile.flush()
            time.sleep(ON_EXCEPTION_WAIT)
                
 
def get_user_timeline(user_id):
    # get the user's timeline or in all likelihood the update to their timeline
    # process those tweets for new mentions/replies 
    # if those users are new.. add those users to the list of nodes to get timelines for... mark these nodes with the orginal usernames rank + 1...
    # if the user is already in the database check if thier rank is currently >= thisuserrank + 1 if so reduce their rank to thisuserrank + 1
    latest = None   # most recent id scraped

    try:
        last_tweet = timelines.find({'user.id':user_id}, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
        if last_tweet:
            latest = last_tweet['id']
            # print str(latest)
    except Exception, e:
        pass
        #print "Warning retrieving tweets. username not found or database probably needs to be populated before it can be queried." + str(e)
    
    while True:
        try:
            print "querying twitter for:" + str(user_id)

            newest = None # this is just a flag to let us know if we should update the "latest" value
            #params = {'screen_name':'anasecretss', 'since_id':latest}
            # print "latest = " + str(latest)
            # latest = 0
            params = {'count':GET_USER_TIMELINE_COUNT, 'contributor_details':True, 'id':user_id, 'since_id':latest, 'include_rts':1}
            #params = {'count':200, 'contributor_details':True, 'since_id':latest}
            
            handle_rate_limiting()
            #home = twitter.get_home_timeline(**params)
            home = timeline_twitter.get_user_timeline(**params)
            
            if home:
                while home:
                    store_tweets(home)
     
                    # Only update "latest" if we're inside the first pass through the inner while loop
                    if newest is None:
                        newest = True
                        latest = home[0]['id']
     
                    params['max_id'] = home[-1]['id'] - 1
                    handle_rate_limiting()
                    print "querying twitter for:" + str(user_id)
                            
                    home = timeline_twitter.get_user_timeline(**params)
                    
            else: 
                # print "Ran out of tweets for the current username - setting last scrape time and AuthError = False"
                poi.update({'id':user_id},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':False}}, upsert=False)
                return True
     
        except TwythonRateLimitError, e:
            print "Rate-limit exception encountered. Sleeping for before retrying"
            print datetime.datetime.now().time()
            reset = int(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
            wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
            time.sleep(wait)
        except TwythonAuthError, e:
            # most likely this is due to a private user, so its best to give up.
            poi.update({'id':user_id},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
            # poi.update({'id':user_id},{'$set':{"timeline_auth_error_flag": True}}, upsert=False)
            home = None     
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "AUTHERROR\t get_user_timeline(" + str(user_id) + ")\t" + str(e.__class__) +"\t" + str(e) + "\n"
            print error
#            errorfile.write(error)
#            errorfile.flush()
            reset = int(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
            wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
            wait = 60
            print "setting auth error flag true; waiting for: " +  str(wait)
            time.sleep(wait)
            # Give up on this user
            return False
        except TwythonError, e:
            pattern = re.compile('\s+404\s+', re.IGNORECASE)
            match = pattern.search(str(e))
            if match:
                poi.update({'id':user_id},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
                home = None
                reset = int(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
                wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
                wait = 60
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_timeline(" + str(user_id) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(wait) + " before retrying\n" 
                print error            
#                errorfile.write(error)
#                errorfile.flush()
                print "setting auth error flag true; waiting: " +  str(wait)
                time.sleep(wait)
                return False
            else:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_timeline(" + str(user_id) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
#                errorfile.write(error)
#                errorfile.flush()
                # time.sleep(ON_EXCEPTION_WAIT)
                reset = int(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
                wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
                print "waiting till reset: " +  str(wait)
                time.sleep(wait)
                
        except Exception, e:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR\t get_user_timeline(" + str(user_id) + ")\t" + str(e.__class__) +"\t" + str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
            print error            
#            errorfile.write(error)
#            errorfile.flush()
            time.sleep(ON_EXCEPTION_WAIT)

def get_user_timelines():
        while True:
            # print("selecting next person of interest...")
            # selects on the basis of choosing the one that hasn't been updated in a long time.            
            # don't waste time/twitter calls checking if it hasn't been long enough
            try:
                nextpoi = poi.find({'poi_classification': { '$lt': TIMELINE_POI_CLASS_THRESHOLD}, 'timeline_auth_error_flag':False}, sort=[('datetime_last_timeline_scrape',1)]).limit( 1 )[0]     
                next_harvest_due_at = nextpoi['datetime_last_timeline_scrape'] +  MIN_RESOLUTION
                if next_harvest_due_at > datetime.datetime.now():
                    print "no user due to be scraped"
                    # it wont wait till this poi is due to check again, as new poi might be added to the db before that.
                    # set this to about ten minutes.
                    time.sleep(IDLETIME)
                else:
                    print "getting user timeline: " + str(nextpoi['id'])
                    get_user_timeline(nextpoi['id'])
                    # wait a few seconds
                    time.sleep(1)
                    
            except Exception, e:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR" + "\t" + "get_user_timelines()\t" + str(e.__class__) +"\t"+ str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
#                errorfile.write(error)
#                errorfile.flush()
                time.sleep(ON_EXCEPTION_WAIT)
                pass

get_user_timelines()