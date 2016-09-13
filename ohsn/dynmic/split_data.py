# -*- coding: utf-8 -*-
"""
Created on 14:36, 13/09/16

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import ohsn.util.db_util as dbt
import pymongo
import sys
from datetime import datetime


def split_data(dbname, timename, newtimename):
    db = dbt.db_connect_no_auth(dbname)
    oldtime = db[timename]
    newtime = db[newtimename]
    newtime.create_index([('user.id', pymongo.ASCENDING),
                                  ('id', pymongo.DESCENDING)], unique=False)
    newtime.create_index([('id', pymongo.ASCENDING)], unique=True)

    datepoint = datetime(2016, 04, 06)
    for tweet in oldtime.find({'created_at': {"$gte": datepoint}}, no_cursor_timeout=True).sort([('id', -1)]):
        # print tweet
        newtime.insert(tweet)
        oldtime.delete_one({'id': tweet['id']})

if __name__ == '__main__':
    # split_data('ded', 'timeline', 'newtimeline')
    # split_data('drd', 'timeline', 'newtimeline')
    # split_data('dyg', 'timeline', 'newtimeline')
    print sys.argv[1], sys.argv[2], sys.argv[3]
    split_data(sys.argv[1], sys.argv[2], sys.argv[3])


