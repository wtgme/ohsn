# -*- coding: utf-8 -*-
"""
Created on 11:17 AM, 2/13/16

@author: tw

Extract some users from streams as seed
"""

import sys
sys.path.append('..')
import util.db_util as dbt
import pymongo
from api import profiles_check
import datetime
import time


def check_users(stream, user_info):
    while True:
        count = stream.count({'user_extracted': {'$exists': False}})
        if count == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'no new stream, sleep 2 hours'
            time.sleep(2*60*60)
            continue
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'extract users from stream amount:', count
            for tweet in stream.find({'user_extracted':{'$exists': False}},
                                    ['id_str', 'user']).limit(min(100, count)):
                user = tweet['user']
                if profiles_check.check_en(user) == True:
                    try:
                        user_info.insert(user)
                    except pymongo.errors.DuplicateKeyError:
                        pass
                stream.update({'id': int(tweet['id_str'])}, {'$set':{"user_extracted": True
                                                    }}, upsert=False)


# '''Connect db and stream collections'''
db = dbt.db_connect_no_auth('random')
stream = db['stream']
# Extracting users from stream files, add index for id to avoid duplicated users
user_info = db['poi']
user_info.create_index("id", unique=True)
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'extract users from sample streams'

check_users(stream, user_info)