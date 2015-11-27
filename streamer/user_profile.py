# -*- coding: utf-8 -*-
"""
Created on 15:04, 29/10/15

@author: wt

1. Extracting unique twitter users from twitter streaming data

"""
import sys
sys.path.append('..')
import util.db_util as dbt
import util.twitter_util as twutil
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time

# '''Connect db and stream collections'''
db = dbt.db_connect_no_auth('stream')
sample = db['stream_sample']
track = db['stream_track']

# '''Connect to Twitter.com'''
app_id = 0
twitter = twutil.twitter_auth(app_id)

# '''Extracting users from stream files, add index for id to avoid duplicated users'''
sample_poi = db['user_sample']
sample_poi.create_index("id", unique=True)
track_poi = db['user_track']
track_poi.create_index("id", unique=True)

'''Get all documents in stream collections'''
sample_user_list_all = sample.distinct('user.id')
track_user_list_all = track.distinct('user.id')

'''Get all users that have been scraped'''
sample_scrapted_user_list = sample_poi.distinct('id')
track_scrapted_user_list = track_poi.distinct('id')

'''Eliminate the users that have been scraped'''
sample_user_list = list(set(sample_user_list_all) - set(sample_scrapted_user_list))
track_user_list = list(set(track_user_list_all) - set(track_scrapted_user_list))



def handle_rate_limiting():
    global twitter
    global app_id
    while True:
        try:
            rate_limit_status = twitter.get_application_rate_limit_status(resources=['users'])
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

        reset = float(rate_limit_status['resources']['users']['/users/lookup']['reset'])
        remaining = int(rate_limit_status['resources']['users']['/users/lookup']['remaining'])
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


def get_user_info(stream_user_list, user_info):
    global twitter
    global app_id
    list_size = len(stream_user_list)
    while list_size:
        user_ids = []
        for i in xrange(min(100, list_size)):
            user_id = stream_user_list[0]
            user_ids.append(user_id)
            stream_user_list.remove(user_id)
        handle_rate_limiting()
        infos = []
        try:
            infos = twitter.lookup_user(user_id=user_ids)
        except TwythonError as detail:
            if 'No user matches for specified terms' in detail:
                print user_ids
        for info in infos:
            # print info
            # try:
            user_info.insert(info)
            # except pymongo.errors.DuplicateKeyError:
            #     continue
        list_size = len(stream_user_list)


if __name__ == '__main__':
    print 'extract users from sample streams'
    get_user_info(sample_user_list, sample_poi)

    print 'extract users from track streams'
    get_user_info(track_user_list, track_poi)