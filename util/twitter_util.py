# -*- coding: utf-8 -*-
"""
Created on 21:25, 26/10/15

@author: wt
"""

from twython import Twython, TwythonRateLimitError, TwythonAuthError, TwythonError
import ConfigParser


config = ConfigParser.ConfigParser()
config.read('scraper.cfg')

# spin up twitter api
APP_KEY = config.get('credentials', 'app_key')
APP_SECRET = config.get('credentials', 'app_secret')
OAUTH_TOKEN = config.get('credentials', 'oath_token')
OAUTH_TOKEN_SECRET = config.get('credentials', 'oath_token_secret')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()


