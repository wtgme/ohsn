# -*- coding: utf-8 -*-
"""
Created on 20:00, 29/09/16

@author: wt
Trim user objective in tweets
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import db_util as dbt


def trim_user(dbname, timename):
    db = dbt.db_connect_no_auth(dbname)
    time = db[timename]
    for tweet in time.find({'user.screen_name': {'$exists': False}}, no_cursor_timeout=True):
        user = tweet['user']
        # tweet['user'] = {'id': user['id']}
        # print tweet
        time.update_one({'id': tweet['id']}, {'$set':{"user": {'id': user['id']}}}, upsert=False)

if __name__ == '__main__':
    trim_user('fed', 'timeline')

