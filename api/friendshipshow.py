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

app_id_friendship, twitter_friendship = twutil.twitter_auth()

def handle_friendship_rate_limiting():
    global app_id_friendship, twitter_friendship
    while True:
        # print '---------lookup rate handle------------------'
        try:
            rate_limit_status = twitter_friendship.get_application_rate_limit_status(resources=['friendships'])
        except TwythonRateLimitError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Cannot test due to last incorrect connection, change Twitter APP ID'
            twutil.release_app(app_id_friendship)
            app_id_friendship, twitter_friendship = twutil.twitter_change_auth(app_id_friendship)
            continue
        except TwythonAuthError as detail:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Author Error, change Twitter APP ID'
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
            if '110' in str(detail) or '104' in str(detail):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connection timed out, sleep 30 Sec'
                time.sleep(30)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'friendship show Unhandled ERROR, EXIT()', str(detail)
                exit(1)

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
            break


def get_friendship_info(user1, user2):
    global app_id_friendship, twitter_friendship
    while True:
        handle_friendship_rate_limiting()
        try:
            infos = twitter_friendship.show_friendship(source_id=user1, target_id=user2)
            return infos
        except TwythonError as detail:
            if '50' in str(detail):
                time.sleep(10)
                continue
        except Exception as detail:
            if '443' in str(detail):
                time.sleep(30)
                continue
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'get_friendship_info', str(detail)
                break


def generate_network(user_list, filename):
    with open(filename+time.strftime("-%Y%m%d%H%M%S")+'.net') as fw:
        size = len(user_list)
        for i in xrange(size):
            user1 = user_list[i]
            for j in xrange(i+1, size):
                user2 = user_list[j]
                friendships = get_friendship_info(user1, user2)
                if friendships['relationship']['source']['following']:
                    fw.write(str(user2)+'\t'+str(user1)+'\n')
                if friendships['relationship']['source']['followed_by']:
                    fw.write(str(user1)+'\t'+str(user2)+'\n')
