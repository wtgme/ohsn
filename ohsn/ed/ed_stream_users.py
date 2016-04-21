# -*- coding: utf-8 -*-
"""
Created on 15:04, 29/10/15

@author: wt

1. Extracting unique twitter users from twitter streaming data

"""

from ohsn.util import db_util as dbt
import pymongo
from ohsn.api import profiles_check
import datetime
import time



'''
# Connect to Twitter.com
app_id_look = 0
twitter_look = twutil.twitter_auth(app_id_look)

# Get all documents in stream collections
# sample_user_list_all = sample.distinct('user.id')
#
# Get all users that have been scraped
# sample_scrapted_user_list = sample_poi.distinct('id')
#
# Eliminate the users that have been scraped
# sample_user_list = list(set(sample_user_list_all) - set(sample_scrapted_user_list))


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
        except Exception as detail:
            if '110' in str(detail) or '104' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connection timed out, sleep 30 Sec'
                time.sleep(30)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'user lookup in following snowball Unhandled ERROR, EXIT()', str(detail)
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
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + \
                      "\t cannot get user profiles for" , stream_user_list
                return infos
            elif '50' in str(detail):
                time.sleep(10)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'exception', str(detail)
                break

def extract_users(stream, user_info):
    while True:
        count = stream.count({'user_extracted': {'$exists': False}})
        if count == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'no new stream, sleep 2 hours'
            time.sleep(2*60*60)
            continue
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'extract users from stream amount:', count
            user_list = set()
            for user_id in stream.find({'user_extracted':{'$exists': False}},
                                    ['id_str', 'user.id_str']).limit(min(100, count)):
                # print user_id['id_str'], user_id['user']['id_str']
                user_list.add(user_id['user']['id_str'])
                stream.update({'id': int(user_id['id_str'])}, {'$set':{"user_extracted": True
                                                    }}, upsert=False)
            user_profiles = get_users_info([x for x in user_list])
            for prof in user_profiles:
                try:
                    user_info.insert(prof)
                except pymongo.errors.DuplicateKeyError:
                    pass
'''

def check_users(stream, user_info):
    while True:
        count = stream.count({'user_extracted': {'$exists': False}})
        if count == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'no new stream, sleep 2 hours'
            time.sleep(2*60*60)
            continue
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'extract users from stream amount:', count
            for tweet in stream.find({'user_extracted':{'$exists': False}},
                                    ['id_str', 'user']).limit(min(100, count)):
                user = tweet['user']
                if profiles_check.check_ed(user) == True:
                    try:
                        user_info.insert(user)
                    except pymongo.errors.DuplicateKeyError:
                        pass
                stream.update({'id': int(tweet['id_str'])}, {'$set':{"user_extracted": True
                                                    }}, upsert=False)


if __name__ == '__main__':

    # '''Connect db and stream collections'''
    db = dbt.db_connect_no_auth('ed')
    sample = db['stream']
    # Extracting users from stream files, add index for id to avoid duplicated users
    sample_poi = db['stream_users']
    sample_poi.create_index("id", unique=True)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'extract users from sample streams'
    check_users(sample, sample_poi)

