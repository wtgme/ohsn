# -*- coding: utf-8 -*-
"""
Created on 21:25, 26/10/15

@author: wt
"""

from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
import ConfigParser
import os


def twitter_auth():

    config = ConfigParser.ConfigParser()
    print 'CFG: ' + os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'TwitterAPI.cfg')
    config.read(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'TwitterAPI.cfg'))
    # spin up twitter api
    APP_KEY = config.get('credentials', 'app_key')
    APP_SECRET = config.get('credentials', 'app_secret')
    OAUTH_TOKEN = config.get('credentials', 'oath_token')
    OAUTH_TOKEN_SECRET = config.get('credentials', 'oath_token_secret')

    try:
        twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        twitter.verify_credentials()
        return twitter
    except Exception as e:
        print str(e)
        exit(1)

