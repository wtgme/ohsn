# -*- coding: utf-8 -*-
"""
Created on 21:25, 26/10/15

@author: wt


See: https://twython.readthedocs.org/en/latest/usage/starting_out.html#obtain-an-oauth-2-access-token
Twython offers support for both OAuth 1 and OAuth 2 authentication.

The difference:
OAuth 1 is for user authenticated calls (tweeting, following people, sending DMs, etc.)
OAuth 2 is for application authenticated calls (when you don’t want to authenticate a user and make read-only calls to Twitter, i.e. searching, reading a public users timeline)

Since the reset in rate_limit_status is not changed by the time of last test, continual tests are more effective.
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
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1])

# last_change_time = 0.0

def twitter_auth(app_id=0):
    global flags
    # if time.time()-last_change_time < 3:
    #     print 'TOO much unavailable API account, sleep 20s.'
    #     time.sleep(20)
    while flags[app_id] == 0:
        app_id += 1
        app_id = app_id%len(flags)
    flags[app_id] = 0
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Auth with APP ID: ' + str(app_id)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Avaiable IDs: ' + str(flags[:])

    config = ConfigParser.ConfigParser()
    # print 'CFG: ' + os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'TwitterAPI.cfg')
    config.read(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'TwitterAPI.cfg'))
    # spin up twitter api
    APP_KEY = config.get('credentials'+str(app_id), 'app_key')
    APP_SECRET = config.get('credentials'+str(app_id), 'app_secret')
    OAUTH_TOKEN = config.get('credentials'+str(app_id), 'oath_token')
    OAUTH_TOKEN_SECRET = config.get('credentials'+str(app_id), 'oath_token_secret')

    while True:
        try:
            # user auth
            # twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
            # twitter.verify_credentials()

            # app auth
            twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
            ACCESS_TOKEN = twitter.obtain_access_token()
            twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
            # last_change_time = time.time()
            return app_id, twitter
        except TwythonRateLimitError as e:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                  'Sleep 30 sec for next connection', str(e)
            time.sleep(30)
            continue
        except TwythonError as e:
            if '443' in str(e):
                print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + \
                      '443 ERROR: Sleep 30 sec for next connection', str(e)
                time.sleep(30)
                continue
        except (TwythonAuthError, Exception) as e:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Auth Unsucessful', str(e)
            time.sleep(30)
            continue

def twitter_change_auth(index):
    global flags
    index += 1
    index = index%len(flags)
    return twitter_auth(index)

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

# twitter_auth(app_id=0)