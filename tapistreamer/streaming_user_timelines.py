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
from twython import TwythonRateLimitError, TwythonAuthError
import logging
import time
from multiprocessing import Process

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

'''Auth twitter API'''
app_id = 0
twitter = twutil.twitter_auth(app_id)

print 'Connect Twitter.com'

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
    global twitter
    global app_id
    while True:
        try:
            rate_limit_status = twitter.get_application_rate_limit_status(resources=['statuses'])
        except TwythonRateLimitError as detail:
            print 'Cannot test due to last incorrect connection, change Twitter APP ID'
            twutil.release_app(app_id)
            app_id, twitter = twutil.twitter_change_auth(app_id)
            continue
        except TwythonAuthError as detail:
            print 'Author Error, change Twitter APP ID'
            twutil.release_app(app_id)
            app_id, twitter = twutil.twitter_change_auth(app_id)
            continue
        reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0) + 10
            time.sleep(wait)
        else:
            print 'Ready rate to current query'
            break

def get_user_timeline(user_id, collection):
    global reset
    global remaining
    # Get latest tweet ID scrapted in db collection
    latest = None  # the latest tweet ID scraped to avoid duplicate scraping
    try:
        last_tweet = collection.find({'user.id':int(user_id)}).sort([('id', -1)])[0]  # sort: 1 = ascending, -1 = descending
        print 'The latest stored tweet is created at: ' + str(last_tweet['created_at'])
        print 'Timeline count of User ' + user_id +' is ' + str(collection.count({'user.id': int(user_id)}))
        if last_tweet:
            latest = last_tweet['id']
    except IndexError as detail:
        print 'Get latest stored tweet ERROR, maybe a new user ' + str(detail)
        pass

    #  loop to get the timelines of user, and update the reset and remaining
    while True:
        newest = None
        params = {'count': 200, 'contributor_details': True, 'id': user_id, 'since_id': latest, 'include_rts': 1}
        handle_rate_limiting()
        timelines = twitter.get_user_timeline(**params)
        if timelines:
            print 'Start to crawl all timelines of this user ' + user_id
            while timelines:
                store_tweets(timelines, collection)
                if newest is None:
                    newest = True
                    # The largest id in the first timeline
                    latest = timelines[0]['id']
                params['max_id'] = timelines[-1]['id'] - 1
                handle_rate_limiting()
                timelines = twitter.get_user_timeline(**params)
                # reset = float(twitter.get_lastfunction_header('x-rate-limit-reset'))
                # remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
            print 'Get user ' + user_id + ' tweet number: ' + str(collection.count({'user.id':int(user_id)}))
            return True
        else:
            print 'Cannot get timeline of user ' + user_id
            return False

# get_user_timeline('1268510412', sample_time)
def stream_timeline(user_collection, timeline_collection):
    user_count = user_collection.count()
    ids = []
    while len(ids) < 5000:
        rand_id = random.randint(0, user_count)
        while rand_id in ids:
            rand_id = random.randint(0, user_count)
        twitter_user_id = user_collection.find()[rand_id]['id_str']
        if get_user_timeline(twitter_user_id, timeline_collection):
            ids.append(rand_id)

# p1 = Process(target=stream_timeline, args=(sample_user, sample_time)).start()
# p2 = Process(target=stream_timeline, args=(track_user, track_time)).start()
stream_timeline(track_user, track_time)
stream_timeline(sample_user, sample_time)

