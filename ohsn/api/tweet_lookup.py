# -*- coding: utf-8 -*-
"""
Created on 10:58, 15/02/16

@author: wt
Get users' profiles
Returns fully-hydrated user objects for up to 100 users per request,
as specified by comma-separated values passed to the user_id and/or screen_name parameters.
"""

import ohsn.util.twitter_util as twutil
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import pymongo
import time
from itertools import islice


app_id_look_tweet, twitter_look_tweet = twutil.twitter_auth()
lookup_remain_tweet, lookup_lock_tweet = 0, 1


def handle_lookup_tweet_rate_limiting():
    global app_id_look_tweet, twitter_look_tweet
    while True:
        print '---------handle_lookup_rate_limiting------------------'
        try:
            rate_limit_status = twitter_look_tweet.get_application_rate_limit_status(resources=['statuses'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_look_tweet)
            app_id_look_tweet, twitter_look_tweet = twutil.twitter_change_auth(app_id_look_tweet)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_look_tweet)
            app_id_look_tweet, twitter_look_tweet = twutil.twitter_change_auth(app_id_look_tweet)
            continue
        except TwythonError as detail:
            if 'Twitter API returned a 503' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                      '503 ERROE, sleep 30 Sec'
                time.sleep(30)
                continue
        except Exception as detail:
            # if '110' in str(detail) or '104' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connection timed out, sleep 30 Sec' + str(detail)
            time.sleep(30)
            continue
            # else:
            #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'user lookup in following snowball Unhandled ERROR, EXIT()', str(detail)
            #     exit(1)

        reset = float(rate_limit_status['resources']['statuses']['/statuses/lookup']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/lookup']['remaining'])
        # print '------------------------lookup--------------------'
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 20:
                time.sleep(wait)
            else:
                twutil.release_app(app_id_look_tweet)
                app_id_look_tweet, twitter_look_tweet = twutil.twitter_change_auth(app_id_look_tweet)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            return remaining


def get_tweets_info(stream_tweet_list):
    # print len(stream_tweet_list)
    global app_id_look_tweet, twitter_look_tweet, lookup_remain_tweet, lookup_lock_tweet
    while lookup_lock_tweet:
        try:
            lookup_lock_tweet = 0
            # print 'lookup input', stream_user_list
            if lookup_remain_tweet < 1:
                lookup_remain_tweet = handle_lookup_tweet_rate_limiting()
            infos = twitter_look_tweet.lookup_status(id=stream_tweet_list, trim_user=False)
            lookup_remain_tweet -= 1
            lookup_lock_tweet = 1
            # print 'lookup output', infos
            return infos
        except Exception as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t Lookup Exception " + str(detail)
            if 'Twitter API returned a 401 (Unauthorized)' in str(detail) or 'Twitter API returned a 404 (Not Found)' in str(detail):
                lookup_lock_tweet = 1
                return None
            else:
                lookup_lock_tweet = 0
                lookup_remain_tweet = handle_lookup_tweet_rate_limiting()
                lookup_lock_tweet = 1


def retrive_tweets(ids):
    return get_tweets_info(ids)

def retrive_tweet(filename):
    fo = open(filename, 'r')
    fw = open('tweet.txt', 'w')
    while True:
        lines = list(islice(fo, 100))
        if lines:
            ids = []
            labels = {}
            for line in lines:
                tokens = line.strip().split(',')
                tid = ((tokens[-1][1:-1]))
                ids.append(tid)
                labels[tid] = (tokens[0][1:-1], tokens[1][1:-1])
            tweets = get_tweets_info(ids)
            # print len(tweets)
            for tweet in tweets:
                label = labels[tweet['id_str']]
                fw.write((tweet['id_str'] + '\t' + label[0] +'\t' +label[1]+'\t'+ ' '.join(tweet['text'].split())+'\n').encode('utf-8'))
        if not lines:
            break
    fw.flush()
    fw.close()
    fo.close()



if __name__ == '__main__':
    retrive_tweet('corpus.csv')