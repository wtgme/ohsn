# -*- coding: utf-8 -*-
"""
Created on 10:58, 15/02/16

@author: wt
"""

import sys
sys.path.append('..')
import util.twitter_util as twutil
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time

app_id_look, twitter_look = twutil.twitter_auth()
lookup_remain = 0


def handle_lookup_rate_limiting():
    global app_id_look, twitter_look
    while True:
        print '---------handle_lookup_rate_limiting------------------'
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
        except Exception as detail:
            # if '110' in str(detail) or '104' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connection timed out, sleep 30 Sec' + str(detail)
            time.sleep(30)
            continue
            # else:
            #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'user lookup in following snowball Unhandled ERROR, EXIT()', str(detail)
            #     exit(1)

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
            return remaining


def get_users_info(stream_user_list):
    global app_id_look, twitter_look, lookup_remain
    infos = []
    while True:
        try:
            if lookup_remain == 0:
                lookup_remain = handle_lookup_rate_limiting()
            infos = twitter_look.lookup_user(user_id=stream_user_list)
            lookup_remain -= 1
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
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), \
                    'get_users_info_exception', str(detail)
                break