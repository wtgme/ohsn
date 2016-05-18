# -*- coding: utf-8 -*-
"""
Created on 17:32, 25/02/16

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import datetime
import pymongo
from ohsn.api import timelines
from ohsn.api import lookup, following
from ohsn.util import db_util as dbt
import time
from threading import Thread
import pickle, math
import os.path


def getuid(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    sample_user = db[colname]
    uids = list()
    for user in sample_user.find({'level': 1}, ['id']):
        uids.append(user['id'])
    return uids


def seed():
    db = dbt.db_connect_no_auth('ded')
    sample_user = db['com']
    # neiblist = pickle.load(open('ygtimeuid.pick', 'r'))
    neiblist = getuid('fed', 'com')
    list_size = len(neiblist)
    print list_size
    length = int(math.ceil(list_size/100.0))
    for index in xrange(length):
        index_begin = index*100
        index_end = min(list_size, index_begin+100)
        lookup.lookup_user_list(neiblist[index_begin:index_end], sample_user, 1, 'N')


def monitor_network(time_index):
    datasets = ['ded', 'drd', 'dyg']
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl networks'
    for dataset in datasets:
        db = dbt.db_connect_no_auth(dataset)
        sample_user = db['com']
        sample_net = db['net']
        sample_user.create_index([('id', pymongo.ASCENDING)], unique=True)
        sample_net.create_index([('scraped_times', pymongo.ASCENDING)], unique=False)
        # crawl the current social network between users in a community
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl networks for ' + dataset
        following.monitor_friendships(sample_user, sample_net, time_index)
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Finish network crawl for ' + dataset

    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Finish networks crawl'


def monitor_timeline(time_index):
    datasets = ['ded', 'drd', 'dyg']
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl timelines'
    for dataset in datasets:
        db = dbt.db_connect_no_auth(dataset)
        sample_user = db['com']
        sample_time = db['timeline']
        sample_user.create_index([('timeline_scraped_times', pymongo.ASCENDING)], unique=False)
        sample_time.create_index([('user.id', pymongo.ASCENDING),
                                  ('id', pymongo.DESCENDING)], unique=False)
        sample_time.create_index([('id', pymongo.ASCENDING)], unique=True)
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl timeline'
        timelines.monitor_timeline(sample_user, sample_time, time_index)
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'Finish a crawl'

    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Finish timlines crawl'


def check_change(time_index):
    db = dbt.db_connect_no_auth('monitor')
    changedb = db['changes']
    changedb.create_index([('dataset', pymongo.ASCENDING),
                         ('statis_index', pymongo.DESCENDING)], unique=True)
    datasets = ['ded', 'drd', 'dyg']
    check_keys = ['description', 'friends_count', 'followers_count', 'statuses_count']
    for dataset in datasets:
        dbs = dbt.db_connect_no_auth(dataset)
        sample_user = dbs['com']
        sample_time = dbs['timeline']
        sample_net = dbs['net']
        changes = {'dataset': dataset, 'statis_index': time_index}
        # check prof changes, 'description', 'friends_count', 'followers_count', 'statuses_count'
        for user in sample_user.find({'timeline_scraped_times': time_index, 'timeline_count': {'$gt': 0}}):
            # print dataset, user['id']
            last_tweet = sample_time.find({'user.id': user['id']},
                                          {'id':1, 'user':1, 'created_at':1}).sort([('id', -1)]).limit(1)[0]  # sort: 1 = ascending, -1 = descending
            if last_tweet:
                userc = last_tweet['user']
                # print last_tweet['id']
                for key in check_keys:
                    if user[key] != userc[key]:
                        value = changes.get(key, 0)
                        value += 1
                        changes[key] = value
                        sample_user.update_one({'id': user['id']}, {'$set': {key: userc[key]}}, upsert=False)
                        if 'count' in key:
                            if user[key] < userc[key]:
                                value = changes.get(key+'_inc', 0)
                                value += 1
                                changes[key+'_inc'] = value
                            elif user[key] > userc[key]:
                                value = changes.get(key+'_dec', 0)
                                value += 1
                                changes[key+'_dec'] = value

        # check following changes among users

        count = sample_net.count({'scraped_times': time_index})-sample_net.count({'scraped_times': time_index-1})
        changes['net_changes'] = count
        changes['statis_at'] = datetime.datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y')
        try:
            changedb.insert(changes)
        except pymongo.errors.DuplicateKeyError:
            pass


def start_monitor():
    if os.path.isfile('index.pick'):
        index = pickle.load(open('index.pick', 'r'))
    else:
        index = 1
    while True:
        start = time.time()
        t1 = Thread(target=monitor_network, args=[index])
        t2 = Thread(target=monitor_timeline, args=[index])
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        check_change(index)
        finish = time.time()
        during = finish - start
        print 'TIME TO FINISH ONE MONITOR', during
        time.sleep(24*60*60.0 - during)
        index += 1
        pickle.dump(index, open('index.pick', 'w'))


def fill_network(time_index):
    datasets = ['yg']
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl networks'
    for dataset in datasets:
        db = dbt.db_connect_no_auth(dataset)
        sample_user = db['tcom']
        sample_net = db['tnet']
        sample_user.create_index([('id', pymongo.ASCENDING)], unique=True)
        sample_net.create_index([('scraped_times', pymongo.ASCENDING)], unique=False)
        # crawl the current social network between users in a community
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl networks for ' + dataset
        following.monitor_friendships(sample_user, sample_net, time_index)
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Finish network crawl for ' + dataset

    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Finish networks crawl'

# fill_network(1)

start_monitor()



# if __name__ == '__main__':
#     print 'Job starts.......'
#     index = 1
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(start_monitor, 'interval', hours=24)
#     scheduler.start()
#     print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
#     try:
#         # This is here to simulate application activity (which keeps the main thread alive).
#         while True:
#             time.sleep(2)
#     except (KeyboardInterrupt, SystemExit):
#         # Not strictly necessary if daemonic mode is enabled but should be done if possible
#         scheduler.shutdown()
