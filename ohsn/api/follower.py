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
    The type field is not used in dynamic monitors.

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


app_id_follower, twitter_follower = twutil.twitter_auth()
follower_remain, follower_lock = 0, 1


def handle_follower_rate_limiting():
    global app_id_follower, twitter_follower
    while True:
        print '---------handle_follower_rate_limiting------------------'
        try:
            rate_limit_status = twitter_follower.get_application_rate_limit_status(resources=['followers'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_follower)
            app_id_follower, twitter_follower = twutil.twitter_change_auth(app_id_follower)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_follower)
            app_id_follower, twitter_follower = twutil.twitter_change_auth(app_id_follower)
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
                  'Connection timed out, sleep 30 Sec', str(detail)
            time.sleep(30)
            continue
            # else:
            #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'handle_follower_rate_limiting Unhandled ERROR, EXIT()', str(detail)
            #     exit(2)

        reset = float(rate_limit_status['resources']['followers']['/followers/ids']['reset'])
        remaining = int(rate_limit_status['resources']['followers']['/followers/ids']['remaining'])
        # print '------------------------following--------------------'
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 20:
                time.sleep(wait)
            else:
                twutil.release_app(app_id_follower)
                app_id_follower, twitter_follower = twutil.twitter_change_auth(app_id_follower)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            return remaining


def get_followers(params):
    global app_id_follower, twitter_follower, follower_remain, follower_lock
    while follower_lock:
        try:
            follower_lock = 0
            if follower_remain < 1:
                follower_remain = handle_follower_rate_limiting()
            followers = twitter_follower.get_followers_ids(**params)
            follower_remain -= 1
            follower_lock = 1
            return followers
        except Exception as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t Follower Exception " + str(detail)
            if 'Twitter API returned a 401 (Unauthorized)' in str(detail) or 'Twitter API returned a 404 (Not Found)' in str(detail):
                follower_lock = 1
                return None
            else:
                follower_lock = 0
                follower_remain = handle_follower_rate_limiting()
                follower_lock = 1
                continue


def snowball_follower(poi_db, net_db, level, check='N'):
    #Processing max 200 users each time.
    start_level = level
    while True:
        count = poi_db.find_one({'level': start_level,
                              'protected': False,
                              'follower_scrape_flag': {'$exists': False}})
        if count is None:
            return False
        else:
            for user in poi_db.find({'level': start_level, 'protected': False,
                                     'follower_scrape_flag': {'$exists': False}},
                                    ['id_str']).limit(200):
                next_cursor = -1
                params = {'user_id': user['id_str'], 'count': 5000, 'stringify_ids':True}
                # follower getting
                while next_cursor != 0:
                    params['cursor'] = next_cursor
                    followers = get_followers(params)
                    if followers:
                        follower_ids = followers['ids']
                        list_size = len(follower_ids)
                        length = int(math.ceil(list_size/100.0))
                        # print length
                        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Process followers', list_size, 'for user', user['id_str']
                        for index in xrange(length):
                            index_begin = index*100
                            index_end = min(list_size, index_begin+100)
                            profiles = lookup.get_users_info(follower_ids[index_begin:index_end])

                            if profiles:
                                print 'user prof:', index_begin, index_end, len(profiles)
                                for profile in profiles:
                                    check_flag = profiles_check.check_user(profile, check)
                                    if check_flag:
                                        profile['follower_prelevel_node'] = user['id_str']
                                        profile['level'] = start_level+1
                                        try:
                                            poi_db.insert(profile)
                                        except pymongo.errors.DuplicateKeyError:
                                            pass
                                        try:
                                            net_db.insert({'user': int(user['id_str']), 'follower': int(profile['id_str']),
                                                       'scraped_at': datetime.datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y')})
                                        except pymongo.errors.DuplicateKeyError:
                                            pass
                    # prepare for next iterator
                        next_cursor = followers['next_cursor']
                    else:
                        break
                poi_db.update_one({'id': int(user['id_str'])}, {'$set':{"follower_scrape_flag": True
                                                    }}, upsert=False)
            continue