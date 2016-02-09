# -*- coding: utf-8 -*-
"""
Created on 14:47, 09/02/16

@author: wt

This script is to stream all evens about a user
"""

from twython import TwythonStreamer
import sys
sys.path.append('..')
import util.db_util as dbtuil
import util.twitter_util as twtuil
import datetime
import time
import os
import ConfigParser


class user_stream(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            store_data(data)

    def on_error(self, status_code, data):
        print status_code


def store_data(data, db):
    # data['scrapted_at'] = datetime.datetime.strptime(datetime.datetime.now(), '%a %b %d %H:%M:%S +0000 %Y')
    # db.insert(data)
    print data


# db = dbtuil.db_connect_no_auth('ed')
# col = db['userstream']

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'TwitterAPI.cfg'))

# spin up twitter api
APP_KEY = config.get('credentials1', 'app_key')
APP_SECRET = config.get('credentials1', 'app_secret')
OAUTH_TOKEN = config.get('credentials1', 'oath_token')
OAUTH_TOKEN_SECRET = config.get('credentials1', 'oath_token_secret')
print('loaded configuation')

stream = user_stream(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
stream.user(user_id=[4465792575])