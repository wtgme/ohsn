# -*- coding: utf-8 -*-
"""
Created on 16:19, 12/02/16

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import datetime
import pymongo
from ohsn.api import timelines
from ohsn.util import db_util as dbt


def retrieve_timeline():
    print 'Job starts.......'
    '''Connecting db and user collection'''
    db = dbt.db_connect_no_auth('fed')
    sample_user = db['com']
    sample_time = db['timeline']
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting db well'
    sample_user.create_index([('timeline_scraped_times', pymongo.ASCENDING),
                              ('level', pymongo.ASCENDING)])
    sample_time.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    sample_time.create_index([('id', pymongo.ASCENDING)], unique=True)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connect Twitter.com'
    # stream_timeline(sample_user, sample_time, 1, 2)
    timelines.stream_timeline(sample_user, sample_time, 1, 3)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish timeline for sample users'


def update_timeline(olddbname, oldtimename, newdbname, newcomname, newtimename):
    olddb = dbt.db_connect_no_auth(olddbname)
    oldtime = olddb[oldtimename]

    newdb = dbt.db_connect_no_auth(newdbname)
    newtime = newdb[newtimename]
    newcom = newdb[newcomname]

    newcom.create_index([('timeline_scraped_times', pymongo.ASCENDING),
                              ('level', pymongo.ASCENDING)])
    newtime.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    newtime.create_index([('id', pymongo.ASCENDING)], unique=True)

    '''Copy the lastest tweet in old timeline collectin to new timeline collection'''
    for user in newcom.find(no_cursor_timeout=True):
        oldtweets = oldtime.find({'user.id': user['id']}, no_cursor_timeout=True).sort([('id', -1)]).limit(1)
        if oldtweets.count() > 0:
            oldtweet = oldtweets[0]
            try:
                oldtweet['user'] = {'id': user['id']}
                newtime.insert(oldtweet)
            except pymongo.errors.DuplicateKeyError:
                pass

    # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connect Twitter.com'
    # # stream_timeline(sample_user, sample_time, 1, 2)
    # timelines.stream_timeline(newcom, newtime, 1, 3)
    # print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish timeline for sample users'

    # '''Clean the laest tweet of old timeline collection'''
    # for user in newcom.find(no_cursor_timeout=True):
    #     oldtweets = oldtime.find({'user.id': user['id']}, no_cursor_timeout=True).sort([('id', -1)]).limit(1)
    #     if oldtweets.count() > 0:
    #         oldtweet = oldtweets[0]
    #         newtime.delete_one({'id': oldtweet['id']})


if __name__ == '__main__':
    # retrieve_timeline()

    update_timeline('fed', 'timeline', 'fed2', 'com', 'timeline')