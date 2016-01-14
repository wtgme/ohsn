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

app_id_look = 4
twitter_look = twutil.twitter_auth(app_id_look)

app_id_friend = 0
twitter_friend = twutil.twitter_auth(app_id_friend)
com_dic = {}


def handle_lookup_rate_limiting():
    global twitter_look
    global app_id_look
    while True:
        # print '---------lookup rate handle------------------'
        try:
            rate_limit_status = twitter_look.get_application_rate_limit_status(resources=['users'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID'
            twutil.release_app(app_id_look)
            app_id_look, twitter_look = twutil.twitter_change_auth(app_id_look)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID'
            twutil.release_app(app_id_look)
            app_id_look, twitter_look = twutil.twitter_change_auth(app_id_look)
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


def get_following(user_name):
    global twitter_friend
    global app_id_friend
    # print 'a new user'
    next_cursor = -1
    params = {'screen_name': user_name, 'count': 5000}
    # followee getting
    following_ids_list = []
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
                    return following_ids_list
            except TwythonError as detail:
                if 'Received response with content-encoding: gzip' in detail:
                    continue
            except Exception as detail:
                print str(detail)
                break

        followee_ids = followees['ids']
        following_ids_list.extend(followee_ids)
        # prepare for next iterator
        next_cursor = followees['next_cursor']
    return following_ids_list


def get_users_info(stream_user_list):
    global twitter_look
    global app_id_look
    while True:
        handle_lookup_rate_limiting()
        try:
            infos = twitter_look.lookup_user(user_id=stream_user_list)
            return infos
        except TwythonError as detail:
            if 'No user matches for specified terms' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + \
                      "\t cannot get user profiles for" , stream_user_list
                break
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'exception', str(detail)
                break


def filter_noen_user(followee_ids):
    list_size = len(followee_ids)
    followee_names = []
    length = int(math.ceil(list_size/100.0))
    # print length
    for index in xrange(length):
        index_begin = index*100
        index_end = min(list_size, index_begin+100)
        profiles = get_users_info(followee_ids[index_begin:index_end])
        # print 'user profile:', index_begin, index_end, len(profiles)
        for profile in profiles:
            if profile['lang'] != 'en':
                followee_names.append(profile['screen_name'])
    return followee_ids


def commonty(dic_v, list_u):
    comm = 0.0
    for user in list_u:
        val = dic_v.get(user, 0)
        comm += val
    return comm/len(list_u)


def snowball(seed_id):
    following_id_list = get_following(seed_id)
    following_name_list = filter_noen_user(following_id_list)
    for following in following_name_list:
        val = com_dic.get(following, 0)
        val += 1
        com_dic[following] = val

    max_user_name = ''
    max_comm = 0.0
    for following in following_name_list:
        followings_id = get_following(following)
        followings_name = filter_noen_user(followings_id)
        comm = commonty(com_dic, followings_name)
        if comm > max_comm:
            max_comm = comm
            max_user_name = following
    print max_user_name





ed_seed = ['tryingyetdying', 'StonedVibes420', 'thinspo_tinspo']
snowball(ed_seed[0])