# -*- coding: utf-8 -*-
"""
Created on 21:25, 26/10/15

@author: wt
"""

from twython import Twython, TwythonRateLimitError,TwythonError, TwythonAuthError
import ConfigParser
import os
import time
from multiprocessing import Array
import datetime

flags = Array('i', [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1])

def twitter_auth(app_id=0):
    global flags
    flags[app_id] = 0
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Auth with APP ID: ' + str(app_id)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Avaiable IDs: ' + str(flags[:])

    config = ConfigParser.ConfigParser()
    print 'CFG: ' + os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'TwitterAPI.cfg')
    config.read(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'TwitterAPI.cfg'))
    # spin up twitter api
    APP_KEY = config.get('credentials'+str(app_id), 'app_key')
    APP_SECRET = config.get('credentials'+str(app_id), 'app_secret')
    OAUTH_TOKEN = config.get('credentials'+str(app_id), 'oath_token')
    OAUTH_TOKEN_SECRET = config.get('credentials'+str(app_id), 'oath_token_secret')

    while True:
        try:
            twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
            twitter.verify_credentials()
            return twitter
        except TwythonRateLimitError as e:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Sleep 30 sec for next connection'
            time.sleep(30)
            continue
        except TwythonError as e:
            if '443' in str(e):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + '443 ERROR: Sleep 30 sec for next connection'
                time.sleep(30)
                continue
        except TwythonAuthError as e:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Auth Unsucessful'
            exit(1)

def twitter_change_auth(index):
    global flags
    index += 1
    index = index%len(flags)
    while flags[index] == 0:
        index += 1
        index = index%len(flags)
    flags[index] = 0
    return (index, twitter_auth(index))

def release_app(index):
    global flags
    flags[index] = 1


# ida = 1
# idb = 2
# a = twitter_auth(ida)
# b = twitter_auth(idb)
# for i in xrange(10):
#     print '-------------------'
#     release_app(ida)
#     ida, a = twitter_change_auth(ida)
