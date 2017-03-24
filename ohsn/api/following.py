# -*- coding: utf-8 -*-
"""
Created on 12:33, 24/11/15
1. Transform users in seed dbs to poi dbs, and set level = 0
2. Snowball users based on users's following (In Twitter API denoted as friends: https://dev.twitter.com/rest/reference/get/friends/ids)

https://dev.twitter.com/rest/reference/get/users/lookup
users/lookup :This method is especially useful when used in conjunction with collections of user IDs returned from GET friends / ids and GET followers / ids.

net_db:
    user:
    follower:
    type:
        0: following
        1: follower.

@author: wt
"""

import ohsn.util.twitter_util as twutil
import pymongo
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time
import math
import profiles_check
import lookup

app_id_friend, twitter_friend = twutil.twitter_auth()
following_remain, following_lock = 0, 1


def handle_following_rate_limiting():
    global app_id_friend, twitter_friend
    while True:
        print '---------handle_following_rate_limiting------------------'
        try:
            rate_limit_status = twitter_friend.get_application_rate_limit_status(resources=['friends'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_friend)
            app_id_friend, twitter_friend = twutil.twitter_change_auth(app_id_friend)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_friend)
            app_id_friend, twitter_friend = twutil.twitter_change_auth(app_id_friend)
            continue
        except TwythonError as detail:
            # if 'Twitter API returned a 503' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  '503 ERROE, sleep 30 Sec', str(detail)
            time.sleep(30)
            continue
            # else:
            #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Unhandled ERROR, EXIT()', str(detail)
            #     exit(1)
        except Exception as detail:
            # if '110' in str(detail) or '104' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Connection timed out, sleep 30 Sec' + str(detail)
            time.sleep(30)
            continue
            # else:
            #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'handle_follower_rate_limiting Unhandled ERROR, EXIT()', str(detail)
            #     exit(2)

        reset = float(rate_limit_status['resources']['friends']['/friends/ids']['reset'])
        remaining = int(rate_limit_status['resources']['friends']['/friends/ids']['remaining'])
        # print '------------------------following--------------------'
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 20:
                time.sleep(wait)
            else:
                twutil.release_app(app_id_friend)
                app_id_friend, twitter_friend = twutil.twitter_change_auth(app_id_friend)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            return remaining


def get_followings(params):
    global app_id_friend, twitter_friend, following_remain, following_lock
    while following_lock:
        try:
            following_lock = 0
            if following_remain < 1:
                following_remain = handle_following_rate_limiting()
            followees = twitter_friend.get_friends_ids(**params)
            following_remain -= 1
            following_lock = 1
            return followees
        except Exception as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t Following Exception " + str(detail)
            if 'Twitter API returned a 401 (Unauthorized)' in str(detail) or 'Twitter API returned a 404 (Not Found)' in str(detail):
                following_lock = 1
                return None
            else:
                following_lock = 0
                following_remain = handle_following_rate_limiting()
                following_lock = 1
                continue


def snowball_following(poi_db, net_db, level, check='N'):
    #Processing max 200 users each time.
    start_level = level
    while True:
        count = poi_db.find_one({'level': start_level,
                              'protected': False, 
                              'following_scrape_flag': {'$exists': False}})
        if count is None:
            return False
        else:
            # print 'have user', count
            for user in poi_db.find({'level': start_level,
                                     'protected': False,
                                     'following_scrape_flag':
                                         {'$exists': False}},
                                    ['id_str']).limit(200):
                # print 'a new user'
                next_cursor = -1
                params = {'user_id': user['id_str'], 'count': 5000, 'stringify_ids':True}
                # followee getting
                while next_cursor != 0:
                    params['cursor'] = next_cursor
                    followees = get_followings(params)
                    if followees:
                        followee_ids = followees['ids']
                        list_size = len(followee_ids)
                        length = int(math.ceil(list_size/100.0))
                        # print length
                        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Process followings', list_size, 'for user', user['id_str']
                        for index in xrange(length):
                            index_begin = index*100
                            index_end = min(list_size, index_begin+100)
                            profiles = lookup.get_users_info(followee_ids[index_begin:index_end])
                            if profiles:
                                print 'user prof:', index_begin, index_end, len(profiles)
                                for profile in profiles:
                                    check_flag = profiles_check.check_user(profile, check)
                                    if check_flag:
                                        profile['following_prelevel_node'] = user['id_str']
                                        profile['level'] = start_level+1
                                        try:
                                            poi_db.insert(profile)
                                        except pymongo.errors.DuplicateKeyError:
                                            pass
                                        try:
                                            net_db.insert({'user': int(profile['id_str']), 'follower': int(user['id_str']),
                                                       'scraped_at': datetime.datetime.now()})
                                        except pymongo.errors.DuplicateKeyError:
                                            pass
                        # prepare for next iterator
                        next_cursor = followees['next_cursor']
                    else:
                        break
                poi_db.update_one({'id': int(user['id_str'])}, {'$set':{"following_scrape_flag": True
                                                    }}, upsert=False)
            return True


def snowball_following_proportion(poi_db, net_db, level, check='N', proportation=0.1):
    #Processing max 200 users each time., only retrieve 10% followings
    start_level = level
    while True:
        count = poi_db.find_one({'level': start_level,
                              'protected': False,
                              'following_scrape_flag': {'$exists': False}})
        if count is None:
            return False
        else:
            # print 'have user', count
            for user in poi_db.find({'level': start_level,
                                     'protected': False,
                                     'following_scrape_flag':
                                         {'$exists': False}},
                                    ['id_str', 'friends_count']).limit(200):
                # print 'a new user'
                following_limit = int(user['friends_count'] * proportation)
                next_cursor = -1
                params = {'user_id': user['id_str'], 'stringify_ids':True}
                # followee getting
                while next_cursor != 0 and following_limit > 0:
                    params['cursor'] = next_cursor
                    print user['id_str'], ' following limit ', following_limit
                    params['count'] = min(following_limit, 5000)
                    followees = get_followings(params)
                    if followees:
                        followee_ids = followees['ids']
                        list_size = len(followee_ids)
                        following_limit -= list_size
                        length = int(math.ceil(list_size/100.0))
                        # print length
                        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Process followings', list_size, 'for user', user['id_str']
                        for index in xrange(length):
                            index_begin = index*100
                            index_end = min(list_size, index_begin+100)
                            profiles = lookup.get_users_info(followee_ids[index_begin:index_end])
                            if profiles:
                                print 'user prof:', index_begin, index_end, len(profiles)
                                for profile in profiles:
                                    check_flag = profiles_check.check_user(profile, check)
                                    if check_flag:
                                        profile['following_prelevel_node'] = user['id_str']
                                        profile['level'] = start_level+1
                                        try:
                                            poi_db.insert(profile)
                                        except pymongo.errors.DuplicateKeyError:
                                            pass
                                        try:
                                            net_db.insert({'user': int(profile['id_str']), 'follower': int(user['id_str']),
                                                       'scraped_at': datetime.datetime.now()})
                                        except pymongo.errors.DuplicateKeyError:
                                            pass
                        # prepare for next iterator
                        next_cursor = followees['next_cursor']
                    else:
                        break
                poi_db.update_one({'id': int(user['id_str'])}, {'$set':{"following_scrape_flag": True
                                                    }}, upsert=False)
            return True


# ed_seed = ['tryingyetdying', 'StonedVibes420', 'thinspo_tinspo']

def monitor_friendships(sample_user, sample_net, time_index):
    user_set = set()
    for user in sample_user.find({}, ['id']):
        user_set.add(user['id'])
    for user in sample_user.find({'$or': [{'net_scraped_times': {'$exists': False}},
                {'net_scraped_times': {'$lt': time_index}}]}, ['id']):
        userid = user['id']
        next_cursor = -1
        print 'Current processing user:', userid
        params = {'user_id': userid, 'count': 5000}
        while next_cursor != 0:
            params['cursor'] = next_cursor
            followees = get_followings(params)
            if followees:
                followee_ids = followees['ids']
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Monitor Processes followings', len(followee_ids), 'for user', str(userid)
                for followee in followee_ids:
                    if followee in user_set:
                        sample_net.insert({'user': followee, 'follower': userid,
                                           'scraped_times': time_index, 'scraped_at': datetime.datetime.now()})
                next_cursor = followees['next_cursor']
            else:
                break
        sample_user.update_one({'id': userid}, {'$set':{'net_scraped_times': time_index}},
                                   upsert=False)
