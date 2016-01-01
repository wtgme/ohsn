# -*- coding: utf-8 -*-
"""
Created on 20:34, 26/10/15

@author: wt

1. Get the timelines of users in POI
2. Add indexes for collection, in case mongodb consumes too much RAM
        db.poi_sample.createIndex({"id":1})
        db.poi_track.createIndex({"id":1})
        db.poi_sample.createIndex({"timeline_count":1, "timeline_auth_error_flag":-1})
        db.poi_track.createIndex({"timeline_count":1, "timeline_auth_error_flag":-1})

        db.timeline_sample.createIndex( { "user.id" : 1, "id" : -1 } )
        db.timeline_track.createIndex( { "user.id" : 1, "id" : -1 } )

        db.people.getIndexes()

        db.timeline_sample.dropIndex( {"user,id":1 } )
        db.timeline_sample.dropIndex( {"user,id":1, "id":-1 } )
    using limit and project to reduce burden of Mongodb
3. Change Twitter App ID when without engouth rate
4. Target users are those have timelines more than 3000

"""


import sys
sys.path.append('..')
import util.db_util as dbutil
import util.twitter_util as twutil
import datetime
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import time
import pymongo


'''Connecting db and user collection'''
db = dbutil.db_connect_no_auth('stream')
sample_user = db['poi_sample']
track_user = db['poi_track']

sample_user.create_index([('timeline_count', pymongo.ASCENDING),
                         ('timeline_auth_error_flag', pymongo.DESCENDING),
                          ('timeline_scraped_times', pymongo.ASCENDING)])
track_user.create_index([('timeline_count', pymongo.ASCENDING),
                         ('timeline_auth_error_flag', pymongo.DESCENDING),
                         ('timeline_scraped_times', pymongo.ASCENDING)])

sample_user.create_index([('timeline_scraped_times', pymongo.ASCENDING),
                          ('protected', pymongo.ASCENDING),
                          ('timeline_auth_error_flag', pymongo.ASCENDING),
                          ('level', pymongo.ASCENDING)])
track_user.create_index([('timeline_scraped_times', pymongo.ASCENDING),
                         ('protected', pymongo.ASCENDING),
                         ('timeline_auth_error_flag', pymongo.ASCENDING),
                         ('level', pymongo.ASCENDING)])


# set every poi user default flags
# temp = sample_user.find_one({})
# if 'timeline_count' not in temp:
#     print '----------------first time indexing--------------------'
#     sample_user.update({},{'$set':{"timeline_scraped_times": 0,
#                                    "timeline_auth_error_flag" : False,
#                                    "datetime_last_timeline_scrape": None,
#                                    "timeline_count": 0}},
#                        multi=True)
#     track_user.update({},{'$set':{"timeline_scraped_times": 0,
#                                   "timeline_auth_error_flag" : False,
#                                   "datetime_last_timeline_scrape" : None,
#                                   "timeline_count": 0}},
#                       multi=True)

print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connecting db well'
sample_time = db['timeline_sample']
track_time = db['timeline_track']

sample_time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
sample_time.create_index([('id', pymongo.ASCENDING)], unique=True)
track_time.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
track_time.create_index([('id', pymongo.ASCENDING)], unique=True)

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
    try:
        collection.insert(tweets_to_save)
    except pymongo.errors.DuplicateKeyError:
            pass

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
        except TwythonError as detail:
            if 'Twitter API returned a 503' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + '503 ERROE, sleep 30 Sec'
                time.sleep(30)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Unhandled ERROR, EXIT()'
                exit(1)

        reset = float(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'])
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 20:
                time.sleep(wait)
            else:
                twutil.release_app(app_id)
                app_id, twitter = twutil.twitter_change_auth(app_id)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            break

def get_user_timeline(user_id, user_collection, timeline_collection):
    global reset
    global remaining
    # Get latest tweet ID scraped in db collection
    latest = None  # the latest tweet ID scraped to avoid duplicate scraping
    try:
        last_tweet = timeline_collection.find({'user.id':user_id}, {'id':1, 'created_at':1}).sort([('id', -1)]).limit(1)[0]  # sort: 1 = ascending, -1 = descending
        # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Timeline count of User ' + str(user_id) +' is ' + str(timeline_collection.count({'user.id': (user_id)}))
        if last_tweet:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'The latest stored tweet is created at: ' + str(last_tweet['created_at'])
            latest = last_tweet['id']
    except IndexError as detail:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Get latest stored tweet ERROR, maybe a new user ' + str(detail)
        pass

    #  loop to get the timelines of user, and update the reset and remaining
    while True:
        # newest = None
        params = {'count': 200, 'contributor_details': True, 'id': user_id, 'since_id': latest, 'include_rts': 1}
        handle_rate_limiting()
        try:
            timelines = twitter.get_user_timeline(**params)
        except TwythonAuthError:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Fail to access private users'
            # count_scraped = timeline_collection.count({'user.id':user_id})
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'stored user ' + str(user_id) + ' tweet number: ' + str(count_scraped)
            # Scrapt_flag = False
            # if count_scraped > 0:
            #     Scrapt_flag = True
            user_collection.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(),
                                                             'timeline_auth_error_flag': True}},
                                   upsert=False)
            return False
        except TwythonError:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Response was not valid JSON'
            user_collection.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(),
                                                             'timeline_auth_error_flag': True}},
                                   upsert=False)
            return False
        if timelines:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to crawl all timelines of this user ' + str(user_id)
            while timelines:
                store_tweets(timelines, timeline_collection)
                # if newest is None:
                #     newest = True
                #     # The largest id in the first timeline
                #     latest = timelines[0]['id']
                params['max_id'] = timelines[-1]['id'] - 1

                while True:
                    try:
                        handle_rate_limiting()
                        timelines = twitter.get_user_timeline(**params)
                        break
                    except TwythonError as detail:
                        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + str(detail) + ' sleep 20 Sec'
                        time.sleep(20)
                        continue
            # count_scraped = timeline_collection.count({'user.id':user_id})
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Get user ' + str(user_id) + ' tweet number: ' + str(count_scraped)
            ### First Flag is for having scrapted some timelines; Second Flag is for having timeline more than 3000
            user_collection.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(),
                                                             'timeline_auth_error_flag': False}},
                                   upsert=False)
            return True
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Cannot get timeline of user ' + str(user_id)
            # count_scraped = timeline_collection.count({'user.id':user_id})
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'stored user ' + str(user_id) + ' tweet number: ' + str(count_scraped)
            # Scrapt_flag = False
            user_collection.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": datetime.datetime.now(),
                                                             'timeline_auth_error_flag': False}},
                                   upsert=False)
            return False

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

# def stream_timeline(user_collection, timeline_collection):
#     user_collection.create_index([('timeline_count', pymongo.ASCENDING),
#                          ('timeline_auth_error_flag', pymongo.DESCENDING)])
#     count = user_collection.count({"timeline_count": {'$gt': 3000}})
#     # count = 0
#     while True:
#         if count < 5000:
#             print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Get next user to scrape'
#             twitter_user = user_collection.find_one({"timeline_count": 0, 'timeline_auth_error_flag': False},{'id':1})
#             # twitter_user_id = nextpoi['id']
#             print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to scrape user ' + str(twitter_user['id'])
#             get_user_timeline(twitter_user['id'], user_collection, timeline_collection)
#             count = user_collection.count({"timeline_count": {'$gt': 3000}})
#             print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'have desired users number: ' + str(count)
#             # count += 1
#         else:
#             return

def stream_timeline(user_collection, timeline_collection, scrapt_times, level):
    while True:
        count = user_collection.count({'$or':[{'protected': False, 'timeline_scraped_times': {'$exists': False}, 'level': {'$lte': level}},
                                             {'protected': False, 'timeline_scraped_times': {'$lt': scrapt_times}, 'level': {'$lte': level}, 'timeline_auth_error_flag': False}]})
        if count == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'finished'
            break
        else:
            users = user_collection.find({'$or':[{'protected': False, 'timeline_scraped_times': {'$exists': False}, 'level': {'$lte': level}},
                                             {'protected': False, 'timeline_scraped_times': {'$lt': scrapt_times}, 'level': {'$lte': level}, 'timeline_auth_error_flag': False}]},
                                     {'id': 1}).limit(200)
            for user in users:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to scrape user ' + str(user['id'])
                get_user_timeline(user['id'], user_collection, timeline_collection)
                count = user_collection.count({"timeline_count": {'$gt': 3000}})
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'have desired users number: ' + str(count)

                # update timeline_scrapted_times and timeline_count fields
                count_scraped = timeline_collection.count({'user.id': user['id']})
                timeline_scraped_times = user.get('timeline_scraped_times', 0) + 1
                user_collection.update({'id': user['id']}, {'$set':{"timeline_count": count_scraped,
                                                             'timeline_scraped_times': timeline_scraped_times}},
                                   upsert=False)




# p1 = Process(target=stream_timeline, args=(sample_user, sample_time)).start()
# p2 = Process(target=stream_timeline, args=(track_user, track_time)).start()

print 'Job starts.......'
# stream_timeline(sample_user, sample_time, 1, 2)
print 'finish timeline for sample users'
stream_timeline(track_user, track_time, 1, 1)
