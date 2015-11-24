# -*- coding: utf-8 -*-
"""
Created on 12:33, 24/11/15
1. Transform users in seed dbs to poi dbs, and set level = 0
2. Snowball users based on users's following (In Twitter API denoted as friends: https://dev.twitter.com/rest/reference/get/friends/ids)

@author: wt
"""

import sys
sys.path.append('..')
import util.db_util as dbt
import util.twitter_util as twutil
import pymongo
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time


app_id = 4
twitter = twutil.twitter_auth(app_id)

# '''Connect db and stream collections'''
db = dbt.db_connect_no_auth('stream')
sample_seed = db['seed_sample']
track_seed = db['seed_track']

sample_poi = db['poi_sample']
sample_poi.create_index("id", unique=True)
track_poi = db['poi_track']
track_poi.create_index("id", unique=True)

def trans_seed_to_poi(seed_db, poi_db):
    seed_user = seed_db.find({})
    for user in seed_user:
        user['pre_level_node'] = None
        user['level'] = 0
        try:
            poi_db.insert(user)
        except pymongo.errors.DuplicateKeyError:
            pass


def handle_following_rate_limiting():
    global twitter
    global app_id
    while True:
        try:
            rate_limit_status = twitter.get_application_rate_limit_status(resources=['friends'])
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

        reset = float(rate_limit_status['resources']['friends']['/friends/ids']['reset'])
        remaining = int(rate_limit_status['resources']['friends']['/friends/ids']['remaining'])
        # print '------------------------following--------------------'
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 10:
                time.sleep(wait)
            else:
                twutil.release_app(app_id)
                app_id, twitter = twutil.twitter_change_auth(app_id)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            break


def handle_lookup_rate_limiting():
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
        # print '------------------------lookup--------------------'
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 10:
                time.sleep(wait)
            else:
                twutil.release_app(app_id)
                app_id, twitter = twutil.twitter_change_auth(app_id)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            break

def get_users_info(stream_user_list):
    global twitter
    global app_id
    list_size = len(stream_user_list)
    while list_size:
        user_ids = []
        for i in xrange(min(100, list_size)):
            user_id = stream_user_list[0]
            user_ids.append(user_id)
            stream_user_list.remove(user_id)
        handle_lookup_rate_limiting()
        infos = []
        try:
            infos = twitter.lookup_user(user_id=user_ids)
        except TwythonError as detail:
            if 'No user matches for specified terms' in detail:
                print user_ids
        list_size = len(stream_user_list)
    return infos


def snowball_following(poi_db, start_leve):
    global twitter
    global app_id
    start_user_list = poi_db.find({'level': start_leve}, ['id_str'])
    poi_db.create_index([('level', pymongo.ASCENDING), ('pre_level_node', pymongo.ASCENDING)], unique=False)
    for user in start_user_list:
        # print user['id_str']
        params = {'cursor': -1, 'user_id': user['id_str'], 'count': 5000}
        # followee getting
        handle_following_rate_limiting()
        followee_ids = twitter.get_friends_ids(**params)['ids']

        # Eliminate the users that have been scraped
        '''Get all documents in stream collections'''
        user_list_all = poi_db.distinct('id', {'level': start_leve+1, 'pre_level_node': user['id_str']})

        '''Eliminate the users that have been scraped'''
        process_user_list = list(set(followee_ids) - set(user_list_all))
        # print len(followee_ids), len(process_user_list)

        if process_user_list:
            profiles = get_users_info(process_user_list)
            for profile in profiles:
                profile['pre_level_node'] = user['id_str']
                profile['level'] = start_leve+1
                try:
                    poi_db.insert(profile)
                except pymongo.errors.DuplicateKeyError:
                    pass

trans_seed_to_poi(sample_seed, sample_poi)
snowball_following(sample_poi, 0)
trans_seed_to_poi(track_seed, track_poi)
snowball_following(track_poi, 0)
