# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 11:31:14 2015

@author: brendan
"""

import pymongo
from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
# import urllib
import datetime
import time
import re
import subprocess


MONGOURL = 'localhost'
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

APP_KEY    = 'Mfm5oNdGSPMvwhZcB8N4MlsL8'
APP_SECRET = 'C0rbmJP0uKbuF6xcT6aR5vFOV9fS4L1965TKOH97pSqj3NJ1mP'
OAUTH_TOKEN        = '3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
OAUTH_TOKEN_SECRET = 'HUWMfHKyPShE6nH5WXlI26izoQjNtV3US3mNpND1F9qrO'

timeline_twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
timeline_twitter.verify_credentials()

GET_USER_TIMELINE_COUNT = 200
ON_EXCEPTION_WAIT = 60*16
AUTH_ERROR_WAIT = 10
# don't scrape a user more than once every day.
MIN_RESOLUTION = datetime.timedelta(seconds=86400)
# if no poi are due to be harvested wait this long..
# the logic being that if you dynamically add new poi it will spot the new poi in this amount of time and harvest it
IDLETIME = 60*10 # 10 minutes

TIMELINE_POI_CLASS_THRESHOLD = 1

#user_id = 2734355331
#user_id = 535436903
#user_id = 1452532201

# globals to hold the remining calls before waiting
remaining = 0
reset = ON_EXCEPTION_WAIT 

# on program initialisation get current rate info
while True:
    try:
        rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
        reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
        print "user calls reset at " + str(reset)
        print "user calls remaining " +str(remaining)
        break
    except TwythonError, e:
        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate-limit-status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
        print error            
        print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
        time.sleep(ON_EXCEPTION_WAIT)


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
    # print("storing tweets")
    try:
        collection.insert(tweets_to_save)
    except pymongo.errors.DuplicateKeyError:
        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "DuplicateKeyError\t store_tweets()\n"
        print error
        print "Duplicate Tweet: This can happen if the previous scrape was interupted while scraping a user, if not you have a problem"
    
def get_user_timeline(userid, latest=None):
    global remaining
    global reset
    
    # latest = None   # most recent id scraped

    # so we now now how far we got last ime
    # keep trying unless its a certain kind of error
    while True:
        try:
            # check the global counters to see if we have calls left... if not wait
            # print "first user call: if check: remaining = " + str(remaining)
            if remaining <= 1:
                wait = max(reset - time.time(), 0) + 15 # addding 15 second pad     
                #print "first user call: if user_timeline remaining <= 1; waiting " +str(wait) + " seconds for reset"        
                #print datetime.datetime.now().time()            
                time.sleep(wait)
            
            # should be ok now to make a call
        
            #print "first user call: query of twitter for:" + str(userid)
            newest = None # this is just a flag to let us know if we should update the "latest" value
            params = {'count':GET_USER_TIMELINE_COUNT, 'contributor_details':True, 'id':userid, 'since_id':latest, 'include_rts':1}
            #print params
            # Now this may throw a 404, auth, rate-limit, or ordinary exception
            home = timeline_twitter.get_user_timeline(**params)
            # if successfull update the global counters :)

            #print "first user call: SUCCESS home = "
            # print home

            if timeline_twitter.get_lastfunction_header('x-rate-limit-reset') is not None:
                reset = float(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
                remaining = int(timeline_twitter.get_lastfunction_header('x-rate-limit-remaining'))
            else:
                print "twitter.get_lastfunction_header is None!! Waiting on exception"
                time.sleep(ON_EXCEPTION_WAIT)
            #print "first user call: user_timeline reset at " + str(reset)
            #print "first user call: user_timeline remaining = " + str(remaining)
            # time.sleep(1)
            # break out of the while true above.... you successfully got the first call and the cursor data is now in home!
            break
        
        except TwythonRateLimitError, e:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TwythonRateLimitError\t" + str(e.__class__) +"\t" + str(e) + "\n" 
                print error
                print "this shouldn't happen if your using the function headers right, unless twitter are playing silly buggers"
        #        reset = twitter.get_lastfunction_header('x-rate-limit-reset')
        #        remaining = twitter.get_lastfunction_header('x-rate-limit-remaining')
                # loop until you can get a valid rate-limit-status               
                while True:
                    try:               
                        print "getting rate_limit_status..."
                        rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
                        print "rate_limit_status returned..."
                        reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
                        remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
                        print "rate_limit_status: user_timeline reset at " + str(reset)
                        print "rate_limit_status: user_timeline remaining = " + str(remaining)
                        break
                    except TwythonError, e:
                        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate_limit_status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                        print error            
                        print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
                        time.sleep(ON_EXCEPTION_WAIT)
        
        except TwythonAuthError, e:
            # most likely this is due to a private user, so its best to give up.
            poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)            
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "AUTHERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + "\n"
            print error
            print "setting auth error flag true; waiting for: " +  str(AUTH_ERROR_WAIT) + " to not wind up twitter :)"
            time.sleep(AUTH_ERROR_WAIT)
            # this will break out of the while True that is getting the usertimeline
            # it should go on to the next user....        
            return False
        except TwythonError, e:
            pattern = re.compile('\s+404\s+', re.IGNORECASE)
            match = pattern.search(str(e))
            if match:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
                print error            
                wait = 60
                print "setting auth error flag true; waiting: " +  str(wait)
                poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
                time.sleep(wait)
                # this will break out of the while True that is getting the usertimeline
                # it should go on to the next user....        
                return False
            else:                
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
                time.sleep(ON_EXCEPTION_WAIT)
        except Exception, e:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR\t first call of get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
            print error
            time.sleep(ON_EXCEPTION_WAIT)
            print "Program EXITING"
            exit()

    # when the first call succeeds you come here with home inc the cursor data
    # print "calling if home:"
    if home:
        # print "calling while home"
        while home:
            store_tweets(home)
 
            # Only update "latest" if we're inside the first pass through the inner while loop
            if newest is None:
                newest = True
                latest = home[0]['id']
 
            params['max_id'] = home[-1]['id'] - 1
            
            # keep trying unless its a certain kind of error
            while True:
                try:
                    # print "querying twitter for:" + str(userid)                        
                    # check the global counters to see if we have calls left... if not wait
                    # print "iterative user call: if check: remaining = " + str(remaining)
                    if remaining <= 1:
                        wait = max(reset - time.time(), 0) + 15 # addding 15 second pad     
                        #print "iterative user call: if user_timeline remaining <= 1; waiting " +str(wait) + " seconds for reset"        
                        #print datetime.datetime.now().time()            
                        time.sleep(wait)
                    #print "next params = "
                    #print params
                    home = timeline_twitter.get_user_timeline(**params)
                    # if successfull update the global counters :)
                    if timeline_twitter.get_lastfunction_header('x-rate-limit-reset') is not None:
                        reset = float(timeline_twitter.get_lastfunction_header('x-rate-limit-reset'))
                        remaining = int(timeline_twitter.get_lastfunction_header('x-rate-limit-remaining'))
                    else:
                        print "twitter.get_lastfunction_header is None!! Waiting on exception"
                        time.sleep(ON_EXCEPTION_WAIT)
                    #print "iterative user call: user_timeline reset at " + str(reset)
                    #print "iterative user call: user_timeline remaining = " + str(remaining)
                    # time.sleep(1)
                    # break out of the while true:
                    break
                    
                except TwythonRateLimitError, e:
                        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TwythonRateLimitError\t" + str(e.__class__) +"\t" + str(e) + "\n" 
                        print error
                        print "this shouldn't happen if your using the function headers right, unless twitter are playing silly buggers"
                #        reset = twitter.get_lastfunction_header('x-rate-limit-reset')
                #        remaining = twitter.get_lastfunction_header('x-rate-limit-remaining')
                        # loop until you can get a valid rate-limit-status               
                        while True:
                            try:               
                                print "getting rate_limit_status..."
                                rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
                                print "rate_limit_status returned..."
                                reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
                                remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
                                print "rate_limit_status: user_timeline reset at " + str(reset)
                                print "rate_limit_status: user_timeline remaining = " + str(remaining)
                                break
                            except TwythonError, e:
                                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate_limit_status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                                print error            
                                print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
                                time.sleep(ON_EXCEPTION_WAIT)
                
                except TwythonAuthError, e:
                    # most likely this is due to a private user, so its best to give up.
                    poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
                    error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "AUTHERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + "\n"
                    print error
                    
                    print "setting auth error flag true; waiting for: " +  str(AUTH_ERROR_WAIT) + " to not wind up twitter :)"
                    time.sleep(AUTH_ERROR_WAIT)
                    # this will break out of the while True that is getting the usertimeline
                    # it should go on to the next user....        
                    return False
                            
                except TwythonError, e:
                    pattern = re.compile('\s+404\s+', re.IGNORECASE)
                    match = pattern.search(str(e))
                    if match:
                        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
                        print error            
                        wait = 60
                        print "setting auth error flag true; waiting: " +  str(wait)
                        poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
                        time.sleep(wait)
                        # this will break out of the while True that is getting the usertimeline
                        # it should go on to the next user....        
                        return False
                    else:                
                        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                        print error            
                        time.sleep(ON_EXCEPTION_WAIT)
                except Exception, e:
                    error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR\t iterative call of get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n" 
                    print error
                    time.sleep(ON_EXCEPTION_WAIT)
                    print "Program EXITING"
                    exit()
                    
    try:
        # get the id of the last tweet scraped for the user
        # this assumes you got the whole timeline!!!!
        last_tweet = timelines.find({'user.id':userid}, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
        latest = last_tweet['id']
        poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':False, 'timeline_latest_id': latest}}, upsert=False)
    except Exception, e:
        print "EXCEPTION updating poi timeline scrape status"
        print "maybe last-tweet doesn't exist - setting last scrape time and AuthError = False"
        try:
            poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':False}}, upsert=False)
        except Exception, e:
            print "EXCEPTION updating poi timeline scrape status without latest id"
            print "Program EXITING"
            exit()

    return True

def get_disk_utilisation(filename = "disk-space-check.file"):
        df = subprocess.Popen(["df", filename], stdout=subprocess.PIPE)
        output = df.communicate()[0]
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
        percent = float(percent[:-1])

def check_disk_space_and_wait(maxpercent=90, sleeptime=60):
    percent = get_disk_utilisation()
    while percent > maxpercent:
        print "Disk utilisation ("+ str(percent) +"%) is above " + str(maxpercent) + "% waiting till it is reduced"
        time.sleep(sleeptime)           
        percent = get_disk_utilisation()

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
                    get_user_timeline(nextpoi['id'], nextpoi['timeline_latest_id'])
                    # wait a few seconds
                    time.sleep(3)
                    # db.command("collstats", TIMELINES_COL)
                    check_disk_space_and_wait()
                    
            except Exception, e:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR" + "\t" + "get_user_timelines()\t" + str(e.__class__) +"\t"+ str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n" 
                print error            
#                errorfile.write(error)
#                errorfile.flush()
                time.sleep(ON_EXCEPTION_WAIT)
                pass

print "program main"
get_user_timelines()
# get_user_timeline(user_id)
exit()




#
##status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])
### print status
##print "rate-limit-call"
##print twitter.get_lastfunction_header('x-rate-limit-reset')
##print twitter.get_lastfunction_header('x-rate-limit-remaining')
#
#response = twitter.get_followers_ids(user_id=userid, count=10, cursor = -1)
#print "followers-call"
#print twitter.get_lastfunction_header('x-rate-limit-reset')
#print twitter.get_lastfunction_header('x-rate-limit-remaining')
#
##status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])
##print "rate-limit-call"
##print twitter.get_lastfunction_header('x-rate-limit-reset')
##print twitter.get_lastfunction_header('x-rate-limit-remaining')
#
#response = twitter.get_friends_ids(user_id=userid, count=10, cursor = -1)
#print "friends-call"
#print twitter.get_lastfunction_header('x-rate-limit-reset')
#print twitter.get_lastfunction_header('x-rate-limit-remaining')
#
##status = twitter.get_application_rate_limit_status(resources = ['friends', 'followers', 'statuses', 'application'])
##print "rate-limit-call"
#print twitter.get_lastfunction_header('x-rate-limit-reset')
#print twitter.get_lastfunction_header('x-rate-limit-remaining')

## doing the get_user_timeline() call reduces this by one:
#
#resources.statuses
#
#u'/statuses/user_timeline': {u'reset': 1435060035, u'limit': 180, u'remaining': 178}
#
#resources.followers.
#
#u'/followers/ids': {u'reset': 1435060106, u'limit': 15, u'remaining': 12}}

# for friends this is decremented

# u'/friends/ids'

#
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435060034, u'limit': 180, u'remaining': 172}}, u'friends': {u'/friends/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435060106, u'limit': 15, u'remaining': 13}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435060035, u'limit': 180, u'remaining': 177}, u'/statuses/lookup': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435060782, u'limit': 60, u'remaining': 60}}}}
#POST TIMELINE
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435060034, u'limit': 180, u'remaining': 171}}, u'friends': {u'/friends/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435060106, u'limit': 15, u'remaining': 13}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435060035, u'limit': 180, u'remaining': 176}, u'/statuses/lookup': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435060782, u'limit': 60, u'remaining': 60}}}}
#POST FOLLOWER
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435060034, u'limit': 180, u'remaining': 170}}, u'friends': {u'/friends/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435060106, u'limit': 15, u'remaining': 12}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435060035, u'limit': 180, u'remaining': 176}, u'/statuses/lookup': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435060782, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435060782, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435060782, u'limit': 60, u'remaining': 60}}}}
#
#
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435061505, u'limit': 180, u'remaining': 179}}, u'friends': {u'/friends/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/lookup': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435061505, u'limit': 60, u'remaining': 60}}}}
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435061505, u'limit': 180, u'remaining': 178}}, u'friends': {u'/friends/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435061505, u'limit': 180, u'remaining': 179}, u'/statuses/lookup': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435061505, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435061505, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435061505, u'limit': 60, u'remaining': 60}}}}
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435061505, u'limit': 180, u'remaining': 177}}, u'friends': {u'/friends/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/following/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 14}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435061505, u'limit': 180, u'remaining': 179}, u'/statuses/lookup': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435061506, u'limit': 60, u'remaining': 60}}}}
#{u'rate_limit_context': {u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'}, u'resources': {u'application': {u'/application/rate_limit_status': {u'reset': 1435061505, u'limit': 180, u'remaining': 176}}, u'friends': {u'/friends/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/following/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/friends/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 14}, u'/friends/following/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}}, u'followers': {u'/followers/list': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/followers/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 14}}, u'statuses': {u'/statuses/retweets_of_me': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/retweeters/ids': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/mentions_timeline': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/user_timeline': {u'reset': 1435061505, u'limit': 180, u'remaining': 179}, u'/statuses/lookup': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/oembed': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/show/:id': {u'reset': 1435061506, u'limit': 180, u'remaining': 180}, u'/statuses/friends': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/home_timeline': {u'reset': 1435061506, u'limit': 15, u'remaining': 15}, u'/statuses/retweets/:id': {u'reset': 1435061506, u'limit': 60, u'remaining': 60}}}}
##
#
#
#
#
#
#
#
#















#
#{u'rate_limit_context': {
#u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
#}, 
#    u'resources': {
#        u'application': {
#            u'/application/rate_limit_status': {u'reset': 1435056848, u'limit': 180, u'remaining': 178}
#        }, 
#        u'friends': {
#            u'/friends/list': {u'reset': 1435057041, u'limit': 15, u'remaining': 15}, 
#            u'/friends/following/ids': {u'reset': 1435057041, u'limit': 15, u'remaining': 15}, 
#            u'/friends/ids': {u'reset': 1435057041, u'limit': 15, u'remaining': 15}, 
#            u'/friends/following/list': {u'reset': 1435057041, u'limit': 15, u'remaining': 15}
#        }
#    }
#}
#
#{u'rate_limit_context': {
#u'access_token': u'3034707280-wFGQAF4FGBviaiSguCUdeG36NIQG1uh8qqXTC1G'
#}, 
#u'resources': {
#    u'application': {
#        u'/application/rate_limit_status': {u'reset': 1435056848, u'limit': 180, u'remaining': 177}
#    }, 
#    u'statuses': {
#         u'/statuses/retweets_of_me': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/retweeters/ids': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/mentions_timeline': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/user_timeline': {u'reset': 1435057265, u'limit': 180, u'remaining': 180}, 
#         u'/statuses/lookup': {u'reset': 1435057265, u'limit': 180, u'remaining': 180}, 
#         u'/statuses/oembed': {u'reset': 1435057265, u'limit': 180, u'remaining': 180}, 
#         u'/statuses/show/:id': {u'reset': 1435057265, u'limit': 180, u'remaining': 180}, 
#         u'/statuses/friends': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/home_timeline': {u'reset': 1435057265, u'limit': 15, u'remaining': 15}, 
#         u'/statuses/retweets/:id': {u'reset': 1435057265, u'limit': 60, u'remaining': 60}
#        }
#    }
#}
