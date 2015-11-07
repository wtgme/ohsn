# -*- coding: utf-8 -*-
"""
Created on 20:34, 26/10/15

@author: wt

1. Get the timelines of users in POI

"""

import pymongo
import sys
sys.path.append('..')
import util.db_util as dbutil
import util.twitter_util as twutil
import datetime
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import time


'''Connecting db and user collection'''
db = dbutil.db_connect_no_auth('stream')
sample_user = db['poi_sample']
sample_user.create_index([("id", pymongo.DESCENDING)], unique=True)
track_user = db['poi_track']
track_user.create_index([("id", pymongo.DESCENDING)], unique=True)

# set every poi user default flags
# sample_user.update({},{'$set':{"timeline_scraped_flag": False, "timeline_auth_error_flag" : False, "datetime_last_timeline_scrape" : None, "timeline_count" : 0}}, multi=True)
# track_user.update({},{'$set':{"timeline_scraped_flag": False, "timeline_auth_error_flag" : False, "datetime_last_timeline_scrape" : None, "timeline_count" : 0}}, multi=True)

print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connecting db well'
sample_time = db['timeline_sample']
sample_time.create_index([("id", pymongo.DESCENDING)], unique=True)
track_time = db['timeline_track']
track_time.create_index([("id", pymongo.DESCENDING)], unique=True)
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" +  'Connecting timeline dbs well'

'''Auth twitter API'''
app_id = 0
twitter = twutil.twitter_auth(app_id)

print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connect Twitter.com'

def store_tweets(tweets_to_save, collection):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Size of Stored Timelines: ' + str(len(tweets_to_save))
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
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Cannot test due to last incorrect connection, change Twitter APP ID'
            twutil.release_app(app_id)
            app_id, twitter = twutil.twitter_change_auth(app_id)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Author Error, change Twitter APP ID'
            twutil.release_app(app_id)
            app_id, twitter = twutil.twitter_change_auth(app_id)
            continue
        reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0) + 10
            time.sleep(wait)
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            break

def get_user_timeline(user_id, user_collection, timeline_collection):
    global reset
    global remaining
    # Get latest tweet ID scraped in db collection
    latest = None  # the latest tweet ID scraped to avoid duplicate scraping
    try:
        last_tweet = timeline_collection.find({'user.id':user_id}).sort([('id', -1)])[0]  # sort: 1 = ascending, -1 = descending
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'The latest stored tweet is created at: ' + str(last_tweet['created_at'])
        # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Timeline count of User ' + str(user_id) +' is ' + str(timeline_collection.count({'user.id': (user_id)}))
        if last_tweet:
            latest = last_tweet['id']
    except IndexError as detail:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Get latest stored tweet ERROR, maybe a new user ' + str(detail)
        pass

    #  loop to get the timelines of user, and update the reset and remaining
    while True:
        newest = None
        params = {'count': 200, 'contributor_details': True, 'id': user_id, 'since_id': latest, 'include_rts': 1}
        handle_rate_limiting()
        try:
            timelines = twitter.get_user_timeline(**params)
        except TwythonAuthError:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Fail to access private users'
            user_collection.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True, "timeline_scraped_flag": False, 'timeline_count': 0}}, upsert=False)
            return (False, False)
        if timelines:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to crawl all timelines of this user ' + str(user_id)
            while timelines:
                store_tweets(timelines, timeline_collection)
                if newest is None:
                    newest = True
                    # The largest id in the first timeline
                    latest = timelines[0]['id']
                params['max_id'] = timelines[-1]['id'] - 1
                handle_rate_limiting()
                while True:
                    try:
                        timelines = twitter.get_user_timeline(**params)
                        break
                    except TwythonError as detail:
                        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + str(detail) + ' sleep 20 Sec'
                        time.sleep(20)
                        continue
                # reset = float(twitter.get_lastfunction_header('x-rate-limit-reset'))
                # remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
            count_scraped = timeline_collection.count({'user.id':user_id})
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Get user ' + str(user_id) + ' tweet number: ' + str(count_scraped)
            ### First Flag is for having scrapted some timelines; Second Flag is for having timeline more than 3000
            if count_scraped >= 3000:
                user_collection.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':False, "timeline_scraped_flag": True, 'timeline_count': count_scraped}}, upsert=False)
                return (True, True)
            else:
                user_collection.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':False, "timeline_scraped_flag": True, 'timeline_count': count_scraped}}, upsert=False)
                return (True, False)
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Cannot get timeline of user ' + str(user_id)
            user_collection.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(), 'timeline_auth_error_flag':True, "timeline_scraped_flag": False, 'timeline_count': 0}}, upsert=False)
            return (False, False)

# get_user_timeline('1268510412', sample_time)
# def stream_timeline(user_collection, timeline_collection):
#     user_count = user_collection.count()
#     ids = []
#     count = 0
#     while count < 5000:
#         rand_id = random.randint(0, user_count)
#         while rand_id in ids:
#             rand_id = random.randint(0, user_count)
#         twitter_user_id = user_collection.find()[rand_id]['id_str']
#         flags = get_user_timeline(twitter_user_id, user_collection, timeline_collection)
#         ids.append(rand_id)
#         if flags[0] and flags[1]:
#             count += 1

def stream_timeline(user_collection, timeline_collection):
    # count = user_collection.find({"timeline_count": {'$gt': 3000}}).count()
    count = 0
    while True:
        if count < 5000:
            print 'Get next user to scrape'
            nextpoi = user_collection.find({"timeline_count": 0, 'timeline_auth_error_flag':False}).limit(1)[0]
            twitter_user_id = nextpoi['id']
            print 'Start to scrape user ' + str(twitter_user_id)
            get_user_timeline(twitter_user_id, user_collection, timeline_collection)
            # count = user_collection.find({"timeline_count": {'$gt': 3000}}).count()
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'have desired users number: ' + str(count)
            count += 1
        else:
            return
# p1 = Process(target=stream_timeline, args=(sample_user, sample_time)).start()
# p2 = Process(target=stream_timeline, args=(track_user, track_time)).start()
print 'Job starts.......'
stream_timeline(sample_user, sample_time)
# stream_timeline(track_user, track_time)


