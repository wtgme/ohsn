# -*- coding: utf-8 -*-
"""
Created on 20:34, 26/10/15

@author: wt

1. Get the timelines of users in POI

"""

import random
import sys
sys.path.append('..')
import util.db_util as dbutil
import util.twitter_util as twutil
import datetime
import tweepy

'''Connecting db and user collection'''
db = dbutil.db_connect_no_auth('stream')
sample_user = db['poi_sample']
track_user = db['poi_track']

sample_time = db['timeline_sample']
track_time = db['timeline_track']

'''Sample 5000 users from user collections'''
sample_count = sample_user.count()
track_count = track_user.count()
sample_sample_ids = random.sample(range(sample_count), 5000)
track_sample_ids = random.sample(range(track_count), 5000)

'''Auth twitter API'''
twitter = twutil.twitter_auth()


def store_tweets(tweets_to_save, collection):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    for tw in tweets_to_save:
        tw['created_at'] = datetime.datetime.strptime(tw['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        tw['user']['created_at'] = datetime.datetime.strptime(tw['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        # get pictures in tweet...
    #        if GET_TIMELINE_IMAGES:
    #            get_pictures(tw)
    # print("storing tweets")
    collection.insert(tweets_to_save)


def get_user_timeline(user_id, collection):
    try:
        user_timeline = twitter.get_user_timeline(id=user_id)
        store_tweets(user_timeline, collection)
    except tweepy.TweepError as e:
        print e


def stream_timeline(id_list, user_collection, timeline_collection):
    for rand_id in id_list:
        twitter_user_id = user_collection.find()[rand_id]['id_str']
        get_user_timeline(twitter_user_id, timeline_collection)

stream_timeline(sample_sample_ids, sample_user, sample_time)
stream_timeline(track_sample_ids, track_user, track_time)