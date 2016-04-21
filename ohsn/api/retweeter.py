# -*- coding: utf-8 -*-
"""
Created on 10:03 PM, 3/3/16

@author: tw

Returns a collection of up to 100 user IDs belonging to users 
who have retweeted the tweet specified by the id parameter.
"""

import ohsn.util.twitter_util as twutil
from twython import TwythonRateLimitError, TwythonAuthError, TwythonError
import datetime
import time
import pymongo
import lookup, profiles_check

app_id_retweeter, twitter_retweeter = twutil.twitter_auth()
retweeter_remain, retweeter_lock = 0, 1


def handle_retweeter_rate_limiting():
    global app_id_retweeter, twitter_retweeter
    while True:
        print '---------handle__retweeter_rate_limiting------------------'
        try:
            rate_limit_status = twitter_retweeter.get_application_rate_limit_status(resources=['statuses'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_retweeter)
            app_id_retweeter, twitter_retweeter = twutil.twitter_change_auth(app_id_retweeter)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_retweeter)
            app_id_retweeter, twitter_retweeter = twutil.twitter_change_auth(app_id_retweeter)
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

        reset = float(rate_limit_status['resources']['statuses']['/statuses/retweeters/ids']['reset'])
        remaining = int(rate_limit_status['resources']['statuses']['/statuses/retweeters/ids']['remaining'])
        # print '------------------------lookup--------------------'
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 20:
                time.sleep(wait)
            else:
                twutil.release_app(app_id_retweeter)
                app_id_retweeter, twitter_retweeter = twutil.twitter_change_auth(app_id_retweeter)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            return remaining
        
        
def get_retweeters(params):
    global app_id_retweeter, twitter_retweeter, retweeter_remain, retweeter_lock
    while retweeter_lock:
        try:
            retweeter_lock = 0
            if retweeter_remain < 1:
                retweeter_remain = handle_retweeter_rate_limiting()
            retweeters = twitter_retweeter.get_retweeters_ids(**params)
            retweeter_remain -= 1
            retweeter_lock = 1
            return retweeters
        except Exception as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t timeline Exception " + str(detail)
            if 'Twitter API returned a 401 (Unauthorized)' in str(detail) or 'Twitter API returned a 404 (Not Found)' in str(detail):
                # Protected: "request": "/1.1/followers/ids.json",
                # "error": "Not authorized."
                # No Existing: "code": 34,
                # "message": "Sorry, that page does not exist."
                retweeter_lock = 1
                return None
            else:
                retweeter_lock = 0
                retweeter_remain = handle_retweeter_rate_limiting()
                retweeter_lock = 1
                continue


def get_tweet_retweeters(tweet_id, poi_db, check='N'):
    next_cursor = -1
    params = {'id': tweet_id, 'stringify_ids': True}
    # followee getting
    while next_cursor != 0:
        params['cursor'] = next_cursor
        retweeters = get_retweeters(params)
        if retweeters:
            retweeter_ids = retweeters['ids']
            print 'Retweeters size', len(retweeter_ids)
            profiles = lookup.get_users_info(retweeter_ids)
            # if profiles:
            for profile in profiles:
                check_flag = profiles_check.check_user(profile, check)
                if check_flag:
                    try:
                        poi_db.insert(profile)
                    except pymongo.errors.DuplicateKeyError:
                        pass
        # prepare for next iterator
        next_cursor = retweeters['next_cursor']

