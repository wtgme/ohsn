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


def extract_users(stream, user_info, size):
    csize = user_info.count({})
    while csize < size:
        count = stream.count({'user_extracted': {'$exists': False}})
        if count == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'no new stream, sleep 2 hours'
            time.sleep(2*60*60)
            continue
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'extract users from stream amount:', count, csize, min(1000, count, (size-csize))
            for tweet in stream.find({'user_extracted':{'$exists': False}},
                                    ['id_str', 'user']).limit(min(1000, count, (size-csize))):
                user = tweet['user']
                if profiles_check.check_en(user) == True:
                    try:
                        user_info.insert(user)
                    except pymongo.errors.DuplicateKeyError:
                        pass
                stream.update({'id': int(tweet['id_str'])}, {'$set':{"user_extracted": True
                                                    }}, upsert=False)
        csize = user_info.count({})


# '''Connect db and stream collections'''
db = dbt.db_connect_no_auth('young')
stream = db['stream']
# Extracting users from stream files, add index for id to avoid duplicated users
user_info = db['poi']
user_info.create_index("id", unique=True)
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'extract users from sample streams'

extract_users(stream, user_info, 3393)