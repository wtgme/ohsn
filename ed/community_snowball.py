# -*- coding: utf-8 -*-
"""
Created on 9:11 PM, 1/13/16

Choose a seed user and get his following, select one following
that has the maximum common following with current user.
Add this following into community, then combine their following lists
and weighted as frequency.
Continue this step.

@author: tw
"""


import sys
sys.path.append('..')
import util.twitter_util as twutil
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time
import math


com_dic = {}



def handle_following_rate_limiting():
    global twitter_friend
    global app_id_friend
    while True:
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
            if 'Twitter API returned a 503' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                      '503 ERROE, sleep 30 Sec'
                time.sleep(30)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                      'Unhandled ERROR, EXIT()'
                exit(1)

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


def get_following(user_id):
    global twitter_friend
    global app_id_friend
    # print 'a new user'
    next_cursor = -1
    params = {'user_id': user_id, 'count': 5000}
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
                if 'Twitter API returned a 401' in detail:
                    continue
            except TwythonError as detail:
                if 'Received response with content-encoding: gzip' in detail:
                    continue
            except Exception as detail:
                print str(detail)
                break

        followee_ids = followees['ids']
        list_size = len(followee_ids)
        length = int(math.ceil(list_size/100.0))
        # print length
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Process followings', list_size, 'for user', user['id_str']
        for index in xrange(length):
            index_begin = index*100
            index_end = min(list_size, index_begin+100)
            profiles = get_users_info(followee_ids[index_begin:index_end])
            # print 'user profile:', index_begin, index_end, len(profiles)
            for profile in profiles:
                if profile['lang'] == 'en':
                    profile['following_prelevel_node'] = user['id_str']
                    profile['level'] = start_level+1
                    poi_db.update({'id': int(profile['id_str'])}, {'$set':profile}, upsert=True)
                    net_db.update({'user': int(profile['id_str']), 'follower': int(user['id_str'])},
                                  {'$set':{'scraped_at': datetime.datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y')}},
                                  upsert=True)
        # prepare for next iterator
        next_cursor = followees['next_cursor']
    poi_db.update({'id': int(user['id_str'])}, {'$set':{"following_scrape_flag": True
                                                    }}, upsert=False)

ed_seed = ['tryingyetdying', 'StonedVibes420', 'thinspo_tinspo']