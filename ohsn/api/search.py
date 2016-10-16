# -*- coding: utf-8 -*-
"""
Created on 10:48 AM, 5/26/16

@author: tw

https://dev.twitter.com/docs/api/1.1/get/search/tweets

https://dev.twitter.com/rest/reference/get/search/tweets
https://api.twitter.com/1.1/search/tweets.json?q=%23freebandnames&since_id=24012619984051000&max_id=250126199840518145&result_type=mixed&count=4

"""

import ohsn.util.twitter_util as twutil
import ohsn.util.db_util as dbt
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time
import pymongo

search_app_id, search_twitter = twutil.twitter_auth()
search_remain, search_lock = 0, 1


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


def handle_search_rate_limiting():
    global search_app_id, search_twitter
    print '-------------------handle_search_rate_limiting-----------'
    while True:
        try:
            rate_limit_status = search_twitter.get_application_rate_limit_status(resources=['search'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID', str(detail)
            twutil.release_app(search_app_id)
            search_app_id, search_twitter = twutil.twitter_change_auth(search_app_id)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID', str(detail)
            twutil.release_app(search_app_id)
            search_app_id, search_twitter = twutil.twitter_change_auth(search_app_id)
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

        reset = float(rate_limit_status['resources']['search']['/search/tweets']['reset'])
        remaining = int(rate_limit_status['resources']['search']['/search/tweets']['remaining'])
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 20:
                time.sleep(wait)
            else:
                twutil.release_app(search_app_id)
                search_app_id, search_twitter = twutil.twitter_change_auth(search_app_id)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            return remaining


def search_timeline(params):
    global search_app_id, search_twitter, search_remain, search_lock
    while search_lock:
        try:
            search_lock = 0
            if search_remain < 1:
                search_remain = handle_search_rate_limiting()
            # print 'timeline remaining rate:', timeline_remain
            # print 'x-rate-limit-remaining', timeline_twitter.get_lastfunction_header('x-rate-limit-remaining')
            # print params
            timelines = search_twitter.search(**params)
            search_remain -= 1
            search_lock = 1
            return timelines['statuses']
        except Exception as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t timeline Exception " + str(detail)
            if 'Twitter API returned a 401 (Unauthorized)' in str(detail) or 'Twitter API returned a 404 (Not Found)' in str(detail):
                # Protected: "request": "/1.1/followers/ids.json",
                # "error": "Not authorized."
                # No Existing: "code": 34,
                # "message": "Sorry, that page does not exist."
                search_lock = 1
                return None
            else:
                search_lock = 0
                search_remain = handle_search_rate_limiting()
                search_lock = 1
                continue


def search_query(query, timeline_collection):
    latest = None  # the latest tweet ID scraped to avoid duplicate scraping
    try:
        # crawl the recent timeline to the last stored timeline
        last_tweet = timeline_collection.find({}, {'id':1, 'created_at':1}).sort([('id', -1)]).limit(1)[0]  # sort: 1 = ascending, -1 = descending
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
        params = {'count': 100, 'include_entities': True, 'q': query, 'since_id': latest, 'result_type':'mixed'}
        try:
            timelines = search_timeline(params)
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Fail: TwythonAuthError', str(detail)
            return False
        except TwythonError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'timeline TwythonError', str(detail)
            return False
        if timelines:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Start to crawl all tweets related to query '
            while timelines:
                store_tweets(timelines, timeline_collection)
                params['max_id'] = timelines[-1]['id']-1
                timelines = search_timeline(params)
            return True
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Cannot get tweets related to query '
            return False


if __name__ == '__main__':
    db = dbt.db_connect_no_auth('depression')
    search = db['search']
    search.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    search.create_index([('id', pymongo.ASCENDING)], unique=True)
    search_query('#MyDepressionLooksLike', search)