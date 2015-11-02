# -*- coding: utf-8 -*-
"""
Created on 20:34, 26/10/15

@author: wt

1. Get the timelines of users in POI

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
import pymongo
import re

logging.basicConfig(filename='streaming-warnings.log', level=logging.DEBUG)

'''Connecting db and user collection'''
db = dbutil.db_connect_no_auth('stream')
sample_user = db['poi_sample']
track_user = db['poi_track']
# logging.info('Connecting db well')
print 'Connecting db well'

sample_time = db['timeline_sample_test']
track_time = db['timeline_track_test']
# logging.info('Connecting timeline dbs well')
print 'Connecting timeline dbs well'

'''Sample 5000 users from user collections'''
sample_count = sample_user.count()
track_count = track_user.count()
sample_sample_ids = random.sample(range(sample_count), 5000)
track_sample_ids = random.sample(range(track_count), 5000)
# logging.info('Get random id list ready')
print 'Get random id list ready'

'''Auth twitter API'''
twitter = twutil.twitter_auth()
print 'Connect Twitter.com'

GET_USER_TIMELINE_COUNT = 200
ON_EXCEPTION_WAIT = 60*16
AUTH_ERROR_WAIT = 10
MIN_RESOLUTION = datetime.timedelta(seconds=86400)
IDLETIME = 60*10 # 10 minutes
TIMELINE_POI_CLASS_THRESHOLD = 1
remaining = 0
reset = ON_EXCEPTION_WAIT

def store_tweets(tweets_to_save, collection):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    print 'Size of Stored Timelines: ' + str(len(tweets_to_save))
    for tw in tweets_to_save:
        tw['created_at'] = datetime.datetime.strptime(tw['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        tw['user']['created_at'] = datetime.datetime.strptime(tw['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        # get pictures in tweet...
    #        if GET_TIMELINE_IMAGES:
    #            get_pictures(tw)
    # print("storing tweets")
    collection.insert(tweets_to_save)

# Test rate_limit is OK? If not, sleep till to next reset time
def handle_rate_limiting():
    global reset
    global remaining
    while True:
        try:
            rate_limit_status = twitter.get_application_rate_limit_status(resources=['statuses'])
        except TwythonRateLimitError as detail:
            print 'Cannot test'
            t = random.randint(0, 15*60)
            time.sleep(t)
            continue
        reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print 'Need to wait'
            wait = max(reset - time.time(), 0) + 10
            time.sleep(wait)
        else:
            print 'Ready rate'
            break


def get_user_timeline(user_id, collection):
    global reset
    global remaining
    # Get latest tweet ID scrapted in db collection
    latest = None  # the latest tweet ID scraped
    try:
        last_tweet = collection.find({'user.id':int(user_id)}).sort([('id', -1)])[0]  # sort: 1 = ascending, -1 = descending
        print 'Get the latest stored tweet' + str(last_tweet)
        print 'Timeline count of User ' + user_id +' is ' + str(collection.count({'user.id': int(user_id)}))
        if last_tweet:
            latest = last_tweet['id']
    except IndexError as detail:
        print 'Get latest stored tweet ERROR'
        print detail
        pass

    no_tweets_sleep = 1
    #  loop to get the timelines of user, and update the reset and remaining
    while True:
        # try:
        newest = None
        params = {'count': GET_USER_TIMELINE_COUNT, 'contributor_details': True, 'id': user_id, 'since_id': latest, 'include_rts': 1}
        handle_rate_limiting()
        timelines = twitter.get_user_timeline(**params)
        if timelines:
            print 'Start to crawl all timelines'
            while timelines:
                store_tweets(timelines, collection)
                if newest is None:
                    newest = True
                    latest = timelines[0]['id']
                params['max_id'] = timelines[-1]['id'] - 1
                handle_rate_limiting()
                timelines = twitter.get_user_timeline(**params)
                reset = float(twitter.get_lastfunction_header('x-rate-limit-reset'))
                remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
            print 'Get user ' + user_id + ' tweet number: ' + str(collection.count({'user.id':int(user_id)}))
            break
        else:
            time.sleep(60*no_tweets_sleep)
            break

        # except TwythonRateLimitError as e:
        #     reset = float(twitter.get_lastfunction_header('x-rate-limit-reset'))
        #     wait = max(reset - time.time(), 0) + 10
        #     time.sleep(wait)
        # except Exception as e:
        #     print "Error:" + str(e)
        #     logging.error(str(e))
        #     time.sleep(60*15)

# get_user_timeline('1268510412', sample_time)
def stream_timeline(id_list, user_collection, timeline_collection):
    for rand_id in id_list:
        twitter_user_id = user_collection.find()[rand_id]['id_str']
        get_user_timeline(twitter_user_id, timeline_collection)

stream_timeline(sample_sample_ids, sample_user, sample_time)
stream_timeline(track_sample_ids, track_user, track_time)
