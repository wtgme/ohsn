# -*- coding: utf-8 -*-
"""
Created on 17:32, 25/02/16

@author: wt
"""

import sys
sys.path.append('..')
import datetime
import pymongo
from api import timelines, following
import util.db_util as dbt
import time
from threading import Thread


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
    datasets = ['ded', 'drd', 'dyg']
    check_keys = ['description', 'friends_count', 'followers_count', 'statuses_count']
    for dataset in datasets:
        db = dbt.db_connect_no_auth(dataset)
        sample_user = db['com']
        sample_time = db['timeline']
        changes = {'dataset': dataset}
        # check prof changes, 'description', 'friends_count', 'followers_count', 'statuses_count'
        for user in sample_user.find():
            last_tweet = sample_time.find({'user.id':user['id']},
                                          {'id':1, 'user':1, 'created_at':1}).sort([('id', -1)]).limit(1)[0]  # sort: 1 = ascending, -1 = descending
            userc = last_tweet['user']
            for key in check_keys:
                if user[key] is not userc[key]:
                    value = changes.get(key, 0)
                    value += 1
                    changes[key] = value
        # check following changes among users
        sample_net = db['net']
        count = sample_net.count({'scraped_times': time_index})-sample_net.count({'scraped_times': time_index-1})
        changes['net_changes'] = count
        changes['scraped_at'] = datetime.datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y')
        changedb.insert(changes)


def start_monitor():
    index = 1
    while True:
        start = time.time()
        t1 = Thread(target=monitor_network, args=[index])
        # t2 = Thread(target=monitor_timeline, args=[index])
        t1.start()
        # t2.start()
        t1.join()
        # t2.join()
        check_change(index)
        finish = time.time()
        during = finish - start
        print 'TIME TO FINISH ONE MONITOR', during
        time.sleep(24*60*60.0 - during)
        index += 1


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

fill_network(1)

# start_monitor()



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
