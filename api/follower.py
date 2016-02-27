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


app_id_follower, twitter_follower = twutil.twitter_auth()
follower_remain = 0


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


def snowball_follower(poi_db, net_db, level, check='N'):
    global app_id_follower, twitter_follower, follower_remain
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
                        try:
                            if follower_remain == 0:
                                follower_remain = handle_follower_rate_limiting()
                            followers = twitter_follower.get_followers_ids(**params)
                            follower_remain -= 1
                            break
                        # except TwythonAuthError as detail:
                        #     # https://twittercommunity.com/t/401-error-when-requesting-friends-for-a-protected-user/580
                        #     # if 'Twitter API returned a 401' in detail:
                        #     print 'snowball_follower TwythonAuthError unhandled expcetions', str(detail)
                        #     time.sleep(30)
                        #     continue
                        except (TwythonAuthError, TwythonError) as detail:
                            # if 'Received response with content-encoding: gzip' in detail:
                            print 'snowball_follower TwythonError unhandled expcetions', str(detail)
                            follower_remain = handle_follower_rate_limiting()
                            continue
                        except Exception as detail:
                            print 'snowball_follower unhandled expcetions', str(detail)
                            time.sleep(30)
                            continue
                        #     print 'snowball_follower unhandled expcetions', str(detail)
                        #     break

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
                        profiles = lookup.get_users_info(follower_ids[index_begin:index_end])
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