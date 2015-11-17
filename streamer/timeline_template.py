# -*- coding: utf-8 -*-
"""
Created on 1:11 PM, 10/30/15

@author: wt

"""
import random
import sys
sys.path.append('..')
import util.db_util as dbutil
import util.twitter_util as twutil
import datetime
from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
import logging
import time
import re

logging.basicConfig(filename='timeline.log', level=logging.DEBUG)

'''Connecting db and user collection'''
db = dbutil.db_connect_no_auth('stream')
sample_user = db['poi_sample']
track_user = db['poi_track']
logging.info('Connecting db well')

sample_time = db['timeline_sample']
track_time = db['timeline_track']
logging.info('Connecting timeline dbs well')

'''Sample 5000 users from user collections'''
sample_count = sample_user.count()
track_count = track_user.count()
sample_sample_ids = random.sample(range(sample_count), 5000)
track_sample_ids = random.sample(range(track_count), 5000)
logging.info('Get random id list ready')

'''Auth twitter API'''
twitter = twutil.twitter_auth()
logging.info('Connect Twitter.com')

GET_USER_TIMELINE_COUNT = 200
ON_EXCEPTION_WAIT = 60*16
AUTH_ERROR_WAIT = 10
MIN_RESOLUTION = datetime.timedelta(seconds=86400)
IDLETIME = 60*10  # 10 minutes
TIMELINE_POI_CLASS_THRESHOLD = 1
remaining = 0
reset = ON_EXCEPTION_WAIT

# on program initialisation get current rate info
while True:
    try:
        rate_limit_status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
        reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
        print "user calls reset at " + str(reset)
        print "user calls remaining " + str(remaining)
        break
    except TwythonError, e:
        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR getting rate-limit-status\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n"
        print error
        print "waiting for " + str(ON_EXCEPTION_WAIT)+ " seconds"
        time.sleep(ON_EXCEPTION_WAIT)

def store_tweets(tweets_to_save, collection):
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
    collection.insert(tweets_to_save)

def get_user_timeline(userid, collection):
    global remaining
    global reset

    latest = None   # most recent id scraped

# UNCOMMENT THIS BLOCK
# ------------------------

    try:
        last_tweet = collection.find({'user.id':userid}, sort=[('id',-1)]).limit( 1 )[0] # sort: 1 = ascending, -1 = descending
        if last_tweet:
            latest = last_tweet['id']
            # print str(latest)
    except Exception, e:
        pass
        #print "Error retrieving tweets. Database probably needs to be populated before it can be queried."

#--------------------------

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
            home = twitter.get_user_timeline(**params)
            # if successfull update the global counters :)

            #print "first user call: SUCCESS home = "
            # print home
            reset = float(twitter.get_lastfunction_header('x-rate-limit-reset'))
            remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
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
                        rate_limit_status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
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
            # poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
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
                # poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
                time.sleep(wait)
                # this will break out of the while True that is getting the usertimeline
                # it should go on to the next user....
                return False
            else:
                error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n"
                print error
                time.sleep(ON_EXCEPTION_WAIT)
        except Exception, e:
            error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n"
            print error
            print "Program EXITING"
            exit()

    # when the first call succeeds you come here with home inc the cursor data
    # print "calling if home:"
    if home:
        # print "calling while home"
        while home:
            store_tweets(home, collection)

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
                    home = twitter.get_user_timeline(**params)
                    # if successfull update the global counters :)
                    reset = float(twitter.get_lastfunction_header('x-rate-limit-reset'))
                    remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
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
                                rate_limit_status = twitter.get_application_rate_limit_status(resources = ['statuses', 'application'])
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
                    # poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
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
                        # poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True}}, upsert=False)
                        time.sleep(wait)
                        # this will break out of the while True that is getting the usertimeline
                        # it should go on to the next user....
                        return False
                    else:
                        error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "TWYTHONERROR\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n"
                        print error
                        time.sleep(ON_EXCEPTION_WAIT)
                except Exception, e:
                    error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR\t get_user_timeline(" + str(userid) + ")\t" + str(e.__class__) +"\t" + str(e) + " Non rate-limit exception encountered\n"
                    print error
                    print "Program EXITING"
                    exit()


    # if home is None !!!!
    # print "home from first user call is none/false or we got all the tweets - setting last scrape time and AuthError = False"
    # poi.update({'id':userid},{'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':False}}, upsert=False)
    return True


# def get_user_timelines():
#         while True:
#             # print("selecting next person of interest...")
#             # selects on the basis of choosing the one that hasn't been updated in a long time.
#             # don't waste time/twitter calls checking if it hasn't been long enough
#             try:
#                 nextpoi = poi.find({'poi_classification': { '$lt': TIMELINE_POI_CLASS_THRESHOLD}, 'timeline_auth_error_flag':False}, sort=[('datetime_last_timeline_scrape',1)]).limit( 1 )[0]
#                 next_harvest_due_at = nextpoi['datetime_last_timeline_scrape'] +  MIN_RESOLUTION
#                 if next_harvest_due_at > datetime.datetime.now():
#                     print "no user due to be scraped"
#                     # it wont wait till this poi is due to check again, as new poi might be added to the db before that.
#                     # set this to about ten minutes.
#                     time.sleep(IDLETIME)
#                 else:
#                     print "getting user timeline: " + str(nextpoi['id'])
#                     get_user_timeline(nextpoi['id'])
#                     # wait a few seconds
#                     time.sleep(3)
#
#             except Exception, e:
#                 error = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + "ERROR" + "\t" + "get_user_timelines()\t" + str(e.__class__) +"\t"+ str(e) + "Non rate-limit exception encountered. Sleeping for " + str(ON_EXCEPTION_WAIT) + " before retrying\n"
#                 print error
# #                errorfile.write(error)
# #                errorfile.flush()
#                 time.sleep(ON_EXCEPTION_WAIT)
#                 pass

def stream_timeline(id_list, user_collection, timeline_collection):
    for rand_id in id_list:
        twitter_user_id = user_collection.find()[rand_id]['id_str']
        get_user_timeline(twitter_user_id, timeline_collection)

stream_timeline(sample_sample_ids, sample_user, sample_time)
stream_timeline(track_sample_ids, track_user, track_time)

