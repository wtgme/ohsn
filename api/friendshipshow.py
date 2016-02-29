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

app_id_friendship, twitter_friendship = twutil.twitter_auth(56)
friendships_remain, friendships_lock = 0, 1


def handle_friendship_rate_limiting():
    global app_id_friendship, twitter_friendship
    while True:
        print '---------handle_friendship_rate_limiting------------------'
        try:
            rate_limit_status = twitter_friendship.get_application_rate_limit_status(resources=['friendships'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_friendship)
            app_id_friendship, twitter_friendship = twutil.twitter_change_auth(app_id_friendship)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID', str(detail)
            twutil.release_app(app_id_friendship)
            app_id_friendship, twitter_friendship = twutil.twitter_change_auth(app_id_friendship)
            continue
        except TwythonError as detail:
            if 'Twitter API returned a 503' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                      '503 ERROE, sleep 30 Sec'
                time.sleep(30)
                continue
        except Exception as detail:
            # if '110' in str(detail) or '104' in str(detail):
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Connection timed out, sleep 30 Sec' + str(detail)
            time.sleep(30)
            continue
            # else:
            #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'friendship show Unhandled ERROR, EXIT()', str(detail)
            #     exit(1)

        reset = float(rate_limit_status['resources']['friendships']['/friendships/show']['reset'])
        remaining = int(rate_limit_status['resources']['friendships']['/friendships/show']['remaining'])
        # print '------------------------lookup--------------------'
        # print 'user calls reset at ' + str(reset)
        # print 'user calls remaining ' + str(remaining)
        if remaining == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Need to wait till next reset time'
            wait = max(reset - time.time(), 0)
            if wait < 20:
                time.sleep(wait)
            else:
                twutil.release_app(app_id_friendship)
                app_id_friendship, twitter_friendship = twutil.twitter_change_auth(app_id_friendship)
            continue
        else:
            # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Ready rate to current query'
            return remaining


def get_friendship_info(user1, user2):
    global app_id_friendship, twitter_friendship, friendships_remain, friendships_lock
    while friendships_lock:
        try:
            friendships_lock = 0
            if friendships_remain < 1:
                friendships_remain = handle_friendship_rate_limiting()
            infos = twitter_friendship.show_friendship(source_id=user1, target_id=user2)
            friendships_remain -= 1
            friendships_lock = 1
            return infos
        except Exception as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t Friendships Exception " + str(detail)
            if 'Twitter API returned a 401 (Unauthorized)' in str(detail) or 'Twitter API returned a 404 (Not Found)' in str(detail):
                return None
            else:
                friendships_lock = 0
                friendships_remain = handle_friendship_rate_limiting()
                friendships_lock = 1
                continue
    # while True:
    #     try:
    #         if friendships_remain == 0:
    #             friendships_remain = handle_friendship_rate_limiting()
    #         infos = twitter_friendship.show_friendship(source_id=user1, target_id=user2)
    #         friendships_remain -= 1
    #         return infos
    #     except TwythonError as detail:
    #         if '50' in str(detail):
    #             print 'get_friendship_info TwythonError', str(detail)
    #             time.sleep(10)
    #             continue
    #     except Exception as detail:
    #         if '443' in str(detail):
    #             print 'get_friendship_info 443 Exception', str(detail)
    #             time.sleep(30)
    #             continue
    #         else:
    #             print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'get_friendship_info', str(detail)
    #             break


def generate_network(user_list, filename):
    with open(filename, 'w') as fw:
        size = len(user_list)
        for i in xrange(size):
            user1 = user_list[i]
            for j in xrange(i+1, size):
                user2 = user_list[j]
                print 'Test', i*size+j, user1, user2
                friendships = get_friendship_info(user1, user2)
                if friendships:
                    if friendships['relationship']['source']['following']:
                        print str(user2)+'\t'+str(user1)+'\n'
                        fw.write(str(user2)+'\t'+str(user1)+'\n')
                    if friendships['relationship']['source']['followed_by']:
                        print str(user1)+'\t'+str(user2)+'\n'
                        fw.write(str(user1)+'\t'+str(user2)+'\n')


# print get_friendship_info(726972960, 606011299)