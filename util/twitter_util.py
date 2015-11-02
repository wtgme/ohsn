# -*- coding: utf-8 -*-
"""
Created on 21:25, 26/10/15

@author: wt
"""

from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
import ConfigParser
import os
import time
from multiprocessing import Array, Lock

lock = Lock()  #lock to modify resource
flags = [1, 1, 1, 1]  #resouce list, available app ids

def twitter_auth(app_id=1):
    global lock
    global flags

    lock.acquire()
    flags[app_id] = 0
    lock.release()

    print 'Auth with APP ID: ' + str(app_id)
    print 'Avaiable IDs: ' + str(flags)

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
        except Exception as e:
            print 'Sleep 10 sec for next connection'
            time.sleep(10)
            continue
            # exit(1)

def twitter_change_auth(index):
    global flags
    global lock
    index += 1
    index = index%4
    while lock:
        lock = 0
        while flags[index] == 0:
            index += 1
            index = index%4
        flags[index] = 0
    lock = 1
    return (index, twitter_auth(index))

def release_app(index):
    global flags
    global lock
    while lock:
        lock = 0
        flags[index] = 1
    lock = 1


# ida = 1
# idb = 2
# a = twitter_auth(ida)
# b = twitter_auth(idb)
# for i in xrange(10):
#     print '-------------------'
#     release_app(ida)
#     ida, a = twitter_change_auth(ida)
