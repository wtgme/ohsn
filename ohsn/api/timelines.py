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
since_id: Returns results with an ID greater than (that is, more recent than) the specified ID.
max_id: Returns results with an ID less than (that is, older than) or equal to the specified ID.
Each crawl is the most recent 200 timelines.
Set the oldest one in each crawl as max_id.

SEE: https://unsupervisedlearning.wordpress.com/2014/07/06/scraping-your-twitter-homepage-with-python-and-mongodb/
"""

import ohsn.util.twitter_util as twutil
import datetime
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import time
import pymongo

timeline_app_id, timeline_twitter = twutil.twitter_auth()
timeline_remain, timeline_lock = 0, 1


def store_tweets(tweets_to_save, collection):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Size of Stored Timelines: ' + str(len(tweets_to_save))
    for tweet in tweets_to_save:
        tweet['created_at'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        try:
            collection.insert(tweet)
        except pymongo.errors.DuplicateKeyError:
                pass
    # try:
    #     collection.insert(tweets_to_save)
    # except pymongo.errors.DuplicateKeyError:
    #         pass


# Test rate_limit is OK? If not, sleep till to next reset time
def handle_timeline_rate_limiting():
    global timeline_app_id, timeline_twitter
    print '-------------------handle_timeline_rate_limiting-----------'
    while True:
        try:
            rate_limit_status = timeline_twitter.get_application_rate_limit_status(resources=['statuses'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID', str(detail)
            twutil.release_app(timeline_app_id)
            timeline_app_id, timeline_twitter = twutil.twitter_change_auth(timeline_app_id)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID', str(detail)
            twutil.release_app(timeline_app_id)
            timeline_app_id, timeline_twitter = twutil.twitter_change_auth(timeline_app_id)
            continue
        except TwythonError as detail:
            # if 'Twitter API returned a 503' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  '503 ERROE, sleep 30 Sec' + str(detail)
            time.sleep(30)
            continue
            # else:
            #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Unhandled ERROR, EXIT()', str(detail)
            #     exit(1)
        except Exception as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Timeline Unhandled ERROR, EXIT()', str(detail)
            time.sleep(30)
            continue
            # exit(2)

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
                twutil.release_app(timeline_app_id)
                timeline_app_id, timeline_twitter = twutil.twitter_change_auth(timeline_app_id)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            return remaining


def get_timeline(params):
    global timeline_app_id, timeline_twitter, timeline_remain, timeline_lock
    while timeline_lock:
        try:
            timeline_lock = 0
            if timeline_remain < 1:
                timeline_remain = handle_timeline_rate_limiting()
            # print 'timeline remaining rate:', timeline_remain
            # print 'x-rate-limit-remaining', timeline_twitter.get_lastfunction_header('x-rate-limit-remaining')
            # print params
            timelines = timeline_twitter.get_user_timeline(**params)
            timeline_remain -= 1
            timeline_lock = 1
            return timelines
        except Exception as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t timeline Exception " + str(detail)
            if 'Twitter API returned a 401 (Unauthorized)' in str(detail) or 'Twitter API returned a 404 (Not Found)' in str(detail):
                # Protected: "request": "/1.1/followers/ids.json",
                # "error": "Not authorized."
                # No Existing: "code": 34,
                # "message": "Sorry, that page does not exist."
                timeline_lock = 1
                return None
            else:
                timeline_lock = 0
                timeline_remain = handle_timeline_rate_limiting()
                timeline_lock = 1
                continue


def get_user_timeline(user_id, user_collection, timeline_collection, trim_user=True, max_id=None):
    latest = None  # the latest tweet ID scraped to avoid duplicate scraping
    try:
        # crawl the recent timeline to the last stored timeline
        last_tweet = timeline_collection.find({'user.id':user_id}, {'id':1, 'created_at':1}).sort([('id', -1)]).limit(1)[0]  # sort: 1 = ascending, -1 = descending
        if last_tweet:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'The latest stored tweet is created at: ' + str(last_tweet['created_at'])
            latest = last_tweet['id']
    except IndexError as detail:
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
              'Get latest stored tweet ERROR, maybe a new user ' + str(detail)
        pass

    #  loop to get the timelines of user, and update the reset and remaining
    while True:
        # newest = None
        params = {'count': 200, 'trim_user': trim_user, 'include_rts': True, 'id': user_id, 'since_id': latest, 'max_id': max_id}
        try:
            timelines = get_timeline(params)
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Fail to access private users', str(detail)
            user_collection.update_one({'id': user_id}, {'$set':{"scrape_timeline_at": datetime.datetime.now()}},
                                   upsert=False)
            return False
        except TwythonError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'timeline TwythonError', str(detail)
            user_collection.update_one({'id': user_id}, {'$set':{"scrape_timeline_at": datetime.datetime.now()}},
                                   upsert=False)
            return False
        if timelines:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to crawl all timelines of this user ' + str(user_id)
            while timelines:
                store_tweets(timelines, timeline_collection)
                params['max_id'] = timelines[-1]['id']-1
                timelines = get_timeline(params)
            user_collection.update_one({'id': user_id}, {'$set':{"scrape_timeline_at": datetime.datetime.now()}},
                                   upsert=False)
            return True
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Cannot get timeline of user ' + str(user_id)
            user_collection.update_one({'id': user_id}, {'$set':{"scrape_timeline_at": datetime.datetime.now()}},
                                   upsert=False)
            return False

def retrieve_timeline(user_collection, timeline_collection, max_id = None):
    # level: the end level
    while True:
        count = user_collection.find_one({'timeline_scraped_times': {'$exists': False}})
        if count == None:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'finished'
            break
        else:
            for user in user_collection.find({'timeline_scraped_times': {'$exists': False}},
                                     {'id': 1}).limit(200):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to scrape user ' + str(user['id'])
                old_count = timeline_collection.count({'user.id': user['id']})
                get_user_timeline(user_id=user['id'], user_collection=user_collection, timeline_collection=timeline_collection,
                                  trim_user=True, max_id=max_id)
                # count = user_collection.count({"timeline_count": {'$gt': 3000}})
                # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'have desired users number: ' + str(count)

                # update timeline_scrapted_times and timeline_count fields
                count_scraped = timeline_collection.count({'user.id': user['id']})
                timeline_scraped_times = user.get('timeline_scraped_times', 0) + 1
                user_collection.update_one({'id': user['id']}, {'$set':{"timeline_count": (count_scraped-old_count),
                                                             'timeline_scraped_times': timeline_scraped_times}},
                                   upsert=False)


def stream_timeline(user_collection, timeline_collection, scrapt_times, level):
    # level: the end level
    while True:
        count = user_collection.count({'$or':[{'level': {'$lt': level}, 'timeline_scraped_times': {'$exists': False}},
                                             {'level': {'$lt': level}, 'timeline_scraped_times': {'$lt': scrapt_times}}]})
        if count == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'finished'
            break
        else:
            for user in user_collection.find({'$or':[{'level': {'$lt': level}, 'timeline_scraped_times': {'$exists': False}},
                                             {'level': {'$lt': level}, 'timeline_scraped_times': {'$lt': scrapt_times}}]},
                                     {'id': 1}).limit(200):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to scrape user ' + str(user['id'])
                old_count = timeline_collection.count({'user.id': user['id']})
                get_user_timeline(user['id'], user_collection, timeline_collection)
                # count = user_collection.count({"timeline_count": {'$gt': 3000}})
                # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'have desired users number: ' + str(count)

                # update timeline_scrapted_times and timeline_count fields
                count_scraped = timeline_collection.count({'user.id': user['id']})
                timeline_scraped_times = user.get('timeline_scraped_times', 0) + 1
                user_collection.update_one({'id': user['id']}, {'$set':{"timeline_count": (count_scraped-old_count),
                                                             'timeline_scraped_times': timeline_scraped_times}},
                                   upsert=False)


def monitor_timeline(user_collection, timeline_collection, scrapt_times):
    while True:
        count = user_collection.count({'$or':[{'timeline_scraped_times': {'$exists': False}},
                                             {'timeline_scraped_times': {'$lt': scrapt_times}}]})
        if count == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'finished'
            break
        else:
            for user in user_collection.find({'$or':[{'timeline_scraped_times': {'$exists': False}},
                                             {'timeline_scraped_times': {'$lt': scrapt_times}}]},
                                     {'id': 1}).limit(200):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to scrape user ' + str(user['id'])
                get_user_timeline(user['id'], user_collection, timeline_collection, trim_user=False)
                # count = user_collection.count({"timeline_count": {'$gt': 3000}})
                # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'have desired users number: ' + str(count)

                # update timeline_scrapted_times and timeline_count fields
                count_scraped = timeline_collection.count({'user.id': user['id']})
                # timeline_scraped_times = user.get('timeline_scraped_times', 0) + 1
                user_collection.update_one({'id': user['id']}, {'$set':{"timeline_count": count_scraped,
                                                             'timeline_scraped_times': scrapt_times}},
                                   upsert=False)