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

import sys
sys.path.append('..')
import util.db_util as dbt
import util.twitter_util as twutil
import pymongo
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time
import math
import profiles_preposs


app_id_look = 4
twitter_look = twutil.twitter_auth(app_id_look)

app_id_follower = 0
twitter_follower = twutil.twitter_auth(app_id_follower)


# '''Connect db and stream collections'''
# db = dbt.db_connect_no_auth('ed')
#
# ed_poi = db['poi_ed']
# ed_net = db['net_ed']
#
# ed_poi.create_index("id", unique=True)
# ed_poi.create_index([('level', pymongo.ASCENDING),
#                      ('follower_prelevel_node', pymongo.ASCENDING)],
#                     unique=False)
#
# ed_net.create_index([("user", pymongo.ASCENDING),
#                     ("follower", pymongo.ASCENDING),
#                      ("type", pymongo.ASCENDING)],
#                             unique=True)

def trans_seed_to_poi(seed_list, poi_db):
    infos = []
    try:
        handle_lookup_rate_limiting()
        infos = twitter_look.lookup_user(screen_name=seed_list)
    except TwythonError as detail:
        if 'No user matches for specified terms' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), \
                'No user matches for specified terms', seed_list
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'trans_seed_to_poi',\
                str(detail)
    for profile in infos:
        if profiles_preposs.check_ed(profile):
            profile['follower_prelevel_node'] = None
            profile['level'] = 1
            try:
                poi_db.insert(profile)
            except pymongo.errors.DuplicateKeyError:
                pass
            # poi_db.update({'id': int(profile['id_str'])}, {'$set':profile}, upsert=True)

def handle_lookup_rate_limiting():
    global twitter_look
    global app_id_look
    while True:
        # print '---------lookup rate handle------------------'
        try:
            rate_limit_status = twitter_look.get_application_rate_limit_status(resources=['users'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Cannot test due to last incorrect connection, change Twitter APP ID'
            twutil.release_app(app_id_look)
            app_id_look, twitter_look = twutil.twitter_change_auth(app_id_look)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Author Error, change Twitter APP ID'
            twutil.release_app(app_id_look)
            app_id_look, twitter_look = twutil.twitter_change_auth(app_id_look)
            continue
        except TwythonError as detail:
            if 'Twitter API returned a 503' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + '503 ERROE, sleep 30 Sec'
                time.sleep(30)
                continue
        except Exception as detail:
            if '110' in str(detail) or '104' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connection timed out, sleep 30 Sec'
                time.sleep(30)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'user lookup in follower snowball Unhandled ERROR, EXIT()', str(detail)
                exit(1)

        reset = float(rate_limit_status['resources']['users']['/users/lookup']['reset'])
        remaining = int(rate_limit_status['resources']['users']['/users/lookup']['remaining'])
        # print '------------------------lookup--------------------'
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 20:
                time.sleep(wait)
            else:
                twutil.release_app(app_id_look)
                app_id_look, twitter_look = twutil.twitter_change_auth(app_id_look)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            break


def get_users_info(stream_user_list):
    global twitter_look
    global app_id_look
    infos = []
    while True:
        handle_lookup_rate_limiting()
        try:
            infos = twitter_look.lookup_user(user_id=stream_user_list)
            return infos
        except TwythonError as detail:
            if 'No user matches for specified terms' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + \
                      "\t cannot get user profiles for" , stream_user_list
                return infos
            elif '50' in str(detail):
                time.sleep(10)
                continue
        except Exception as detail:
            if '443' in str(detail):
                time.sleep(30)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'get_users_info_exception', str(detail)
                break


def handle_follower_rate_limiting():
    global twitter_follower
    global app_id_follower
    while True:
        # print '---------follower rate handle------------------'
        try:
            rate_limit_status = twitter_follower.get_application_rate_limit_status(resources=['followers'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Cannot test due to last incorrect connection, change Twitter APP ID'
            twutil.release_app(app_id_follower)
            app_id_follower, twitter_follower = twutil.twitter_change_auth(app_id_follower)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Author Error, change Twitter APP ID'
            twutil.release_app(app_id_follower)
            app_id_follower, twitter_follower = twutil.twitter_change_auth(app_id_follower)
            continue
        except TwythonError as detail:
            if 'Twitter API returned a 503' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + '503 ERROE, sleep 30 Sec'
                time.sleep(30)
                continue
        except Exception as detail:
            if '110' in str(detail) or '104' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connection timed out, sleep 30 Sec'
                time.sleep(30)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'handle_follower_rate_limiting Unhandled ERROR, EXIT()', str(detail)
                exit(1)

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
            break


def snowball_follower(poi_db, net_db, level):
    global twitter_follower
    global app_id_follower
    start_level = level
    while True:
        count = poi_db.count({'level': start_level,
                              'protected': False,
                              'follower_scrape_flag': {'$exists': False}})
        if count == 0:
            return False
        else:
            for user in poi_db.find({'level': start_level, 'protected': False,
                                     'follower_scrape_flag': {'$exists': False}},
                                    ['id_str']).limit(min(200, count)):
                next_cursor = -1
                params = {'user_id': user['id_str'], 'count': 5000}
                # follower getting
                while next_cursor != 0:
                    params['cursor'] = next_cursor
                    while True:
                        handle_follower_rate_limiting()
                        try:
                            followers = twitter_follower.get_followers_ids(**params)
                            break
                        except TwythonAuthError as detail:
                            # https://twittercommunity.com/t/401-error-when-requesting-friends-for-a-protected-user/580
                            if 'Twitter API returned a 401' in detail:
                                continue
                        except TwythonError as detail:
                            if 'Received response with content-encoding: gzip' in detail:
                                continue
                        except Exception as detail:
                            print 'snowball_follower unhandled expcetions', str(detail)
                            break

                    # Eliminate the users that have been scraped
                    # '''Get all documents in stream collections'''
                    # user_list_all = poi_db.distinct('id', {'level': start_level+1, 'follower_prelevel_node': user['id_str']})
                    follower_ids = followers['ids']
                    # '''Eliminate the users that have been scraped'''
                    # process_user_list = list(set(followee_ids) - set(user_list_all))
                    # print len(followee_ids), len(process_user_list)
                    list_size = len(follower_ids)
                    length = int(math.ceil(list_size/100.0))
                    # print length
                    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Process followers', list_size, 'for user', user['id_str']
                    for index in xrange(length):
                        index_begin = index*100
                        index_end = min(list_size, index_begin+100)
                        profiles = get_users_info(follower_ids[index_begin:index_end])
                        # print 'user profile:', index_begin, index_end, len(profiles)
                        for profile in profiles:
                            if profiles_preposs.check_ed(profile):
                                profile['follower_prelevel_node'] = user['id_str']
                                profile['level'] = start_level+1
                                try:
                                    poi_db.insert(profile)
                                except pymongo.errors.DuplicateKeyError:
                                    pass
                                try:
                                    net_db.insert({'user': int(user['id_str']), 'follower': int(profile['id_str']), 'type': 1,
                                               'scraped_at': datetime.datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y')})
                                except pymongo.errors.DuplicateKeyError:
                                    pass
                                # poi_db.update({'id': int(profile['id_str'])}, {'$set':profile}, upsert=True)
                                # net_db.update({'user': int(user['id_str']), 'follower': int(profile['id_str'])},
                                #               {'$set':{'scraped_at': datetime.datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y')}},
                                #               upsert=True)
                    # prepare for next iterator
                    next_cursor = followers['next_cursor']
                poi_db.update({'id': int(user['id_str'])}, {'$set':{"follower_scrape_flag": True
                                                    }}, upsert=False)
            return True

# ed_seed = ['tryingyetdying', 'StonedVibes420', 'thinspo_tinspo']
# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Transform seed to poi'
# trans_seed_to_poi(ed_seed, ed_poi)

# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db 1'
# snowball_follower(ed_poi, ed_net, 1)
# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db 2'
# snowball_follower(ed_poi, ed_net, 2)
# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db 3'
# snowball_follower(ed_poi, ed_net, 3)
# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db 4'
# snowball_follower(ed_poi, ed_net, 4)
# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db 5'
# snowball_follower(ed_poi, ed_net, 5)
# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Snowball followees of seeds for sample db 6'
# snowball_follower(ed_poi, ed_net, 6)
#
# print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Finish-------------------------'