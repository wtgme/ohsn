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
import os
import time
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler


def monitor_network():
    datasets = ['ded', 'drd', 'dyg']
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl networks'
    for dataset in datasets:
        db = dbt.db_connect_no_auth(dataset)
        sample_user = db['com']
        sample_user.create_index([('id', pymongo.ASCENDING)], unique=True)

        user_set = set()
        for user in sample_user.find({},['id']):
            user_set.add(user['id'])

        # crawl the current social network between users in a community
        print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Start to crawl networks for ' + dataset
        timestamp = time.strftime("-%Y%m%d%H%M%S")
        out_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
                               'netfiles', dataset+timestamp+'.net')
        following.monitor_friendships(user_set, out_path)
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


# def check


def start_monitor():
    global index
    Thread(target=monitor_network).start()
    Thread(target=monitor_timeline, args=[index]).start()
    index += 1


if __name__ == '__main__':
    print 'Job starts.......'
    index = 1
    scheduler = BackgroundScheduler()
    scheduler.add_job(start_monitor, 'interval', hours=24)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()