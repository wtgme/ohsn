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
import util.twitter_util as twutil
import pymongo
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time
import math
import profiles_check
import lookup

app_id_friend, twitter_friend = twutil.twitter_auth()


def trans_seed_to_poi(seed_list, poi_db):
    app_id_look, twitter_look = twutil.twitter_auth()
    infos = []
    try:
        # print seed_list
        lookup.handle_lookup_rate_limiting()
        infos = twitter_look.lookup_user(screen_name=seed_list)
        # print infos
    except TwythonError as detail:
        if 'No user matches for specified terms' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), \
                'No user matches for specified terms', seed_list
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'trans_seed_to_poi',\
                str(detail)
    for profile in infos:
        # if profiles_preposs.check_ed(profile):
            # profile['following_prelevel_node'] = None
        if profile['lang'] == 'en' and profile['protected']==False:
            profile['level'] = 1
            # poi_db.update({'id': int(profile['id_str'])}, {'$set':profile}, upsert=True)
            try:
                poi_db.insert(profile)
                seed_list.remove(profile['screen_name'])
            except pymongo.errors.DuplicateKeyError:
                print profile['id_str']
                poi_db.update({'id': int(profile['id_str'])}, {'$set':{"level": 1
                                                    }}, upsert=False)
        else:
            print profile['screen_name'], 'set protected from others'
    print seed_list, 'deleted their accounts'

def handle_following_rate_limiting():
    global app_id_friend, twitter_friend
    while True:
        # print '---------friends rate handle------------------'
        try:
            rate_limit_status = twitter_friend.get_application_rate_limit_status(resources=['friends'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID'
            twutil.release_app(app_id_friend)
            app_id_friend, twitter_friend = twutil.twitter_change_auth(app_id_friend)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID'
            twutil.release_app(app_id_friend)
            app_id_friend, twitter_friend = twutil.twitter_change_auth(app_id_friend)
            continue
        except TwythonError as detail:
            # if 'Twitter API returned a 503' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  '503 ERROE, sleep 30 Sec'
            time.sleep(30)
            continue
            # else:
            #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Unhandled ERROR, EXIT()', str(detail)
            #     exit(1)
        except Exception as detail:
            # if '110' in str(detail) or '104' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connection timed out, sleep 30 Sec' + str(detail)
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
            break


def snowball_following(poi_db, net_db, level, check='N'):
    global app_id_friend, twitter_friend
    start_level = level
    while True:
        count = poi_db.count({'level': start_level, 
                              'protected': False, 
                              'following_scrape_flag': {'$exists': False}})
        if count == 0:
            return False
        else:
            # print 'have user', count
            for user in poi_db.find({'level': start_level,
                                     'protected': False,
                                     'following_scrape_flag':
                                         {'$exists': False}},
                                    ['id_str']).limit(min(200, count)):
                # print 'a new user'
                next_cursor = -1
                params = {'user_id': user['id_str'], 'count': 5000}
                # followee getting
                while next_cursor != 0:
                    params['cursor'] = next_cursor
                    while True:
                        handle_following_rate_limiting()
                        try:
                            followees = twitter_friend.get_friends_ids(**params)
                            break
                        except TwythonAuthError as detail:
                            # https://twittercommunity.com/t/401-error-when-requesting-friends-for-a-protected-user/580
                            # if 'Twitter API returned a 401' in detail:
                            time.sleep(20)
                            continue
                        except TwythonError as detail:
                            # if 'Received response with content-encoding: gzip' in detail:
                            print 'snowball_following TwythonError unhandled exception', str(detail)
                            time.sleep(20)
                            continue
                        except Exception as detail:
                            print 'snowball_following unhandled exception', str(detail)
                            time.sleep(20)
                            continue
                        #     print 'snowball_following unhandled exception', str(detail)
                        #     break

                    # # Eliminate the users that have been scraped
                    # '''Get all documents in stream collections'''
                    # user_list_all = poi_db.distinct('id', {'level': start_level+1, 'following_prelevel_node': user['id_str']})
                    followee_ids = followees['ids']
                    # '''Eliminate the users that have been scraped'''
                    # process_user_list = list(set(followee_ids) - set(user_list_all))
                    # print len(followee_ids), len(process_user_list)
                    # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Process', len(process_user_list), 'in', len(followee_ids), 'friends of user', user['id_str'], 'where', len(user_list_all), 'have been processed'
                    list_size = len(followee_ids)
                    length = int(math.ceil(list_size/100.0))
                    # print length
                    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Process followings', list_size, 'for user', user['id_str']
                    for index in xrange(length):
                        index_begin = index*100
                        index_end = min(list_size, index_begin+100)
                        profiles = lookup.get_users_info(followee_ids[index_begin:index_end])
                        # print 'user profile:', index_begin, index_end, len(profiles)
                        for profile in profiles:
                            if check is 'ED':
                                check_flag = profiles_check.check_ed(profile)
                            elif check is 'YG':
                                check_flag = profiles_check.check_yg(profile)
                            elif check is 'DP':
                                check_flag = profiles_check.check_depression(profile)
                            elif check is 'RD':
                                check_flag = profiles_check.check_rd(profile)
                            else:
                                check_flag = profiles_check.check_en(profile)
                            if check_flag:
                                profile['following_prelevel_node'] = user['id_str']
                                profile['level'] = start_level+1
                                try:
                                    poi_db.insert(profile)
                                except pymongo.errors.DuplicateKeyError:
                                    pass
                                try:
                                    net_db.insert({'user': int(profile['id_str']), 'follower': int(user['id_str']), 'type': 0,
                                               'scraped_at': datetime.datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y')})
                                except pymongo.errors.DuplicateKeyError:
                                    pass
                                # poi_db.update({'id': int(profile['id_str'])}, {'$set':profile}, upsert=True)
                                # net_db.update({'user': int(profile['id_str']), 'follower': int(user['id_str'])},
                                #               {'$set':{'scraped_at': datetime.datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y')}},
                                #               upsert=True)
                    # prepare for next iterator
                    next_cursor = followees['next_cursor']
                poi_db.update({'id': int(user['id_str'])}, {'$set':{"following_scrape_flag": True
                                                    }}, upsert=False)
            return True


# ed_seed = ['tryingyetdying', 'StonedVibes420', 'thinspo_tinspo']
