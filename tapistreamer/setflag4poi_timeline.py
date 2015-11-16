# -*- coding: utf-8 -*-
"""
Created on 15:47, 15/11/15

Set flags of timeline_scraped_flag, timeline_count, datetime_last_timeline_scrape, timeline_auth_error_flag
in poi collection by going through the records in timeline

@author: wt
"""
import sys
sys.path.append('..')
import util.db_util as dbutil
import datetime

'''Connecting db and collections'''
db = dbutil.db_connect_no_auth('stream')
sample_poi = db['poi_sample']
track_poi = db['poi_track']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connecting POI dbs well'

sample_time = db['timeline_sample']
track_time = db['timeline_track']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" +  'Connecting timeline dbs well'


print sample_poi.count({})
print track_poi.count({})


def set_flag_poi_with_timeline(poidb, timelinedb):
    i = 0
    poicursor = poidb.find({})
    for user in poicursor:
        i += 1
        if i%1000 == 0:
            print 'updated number of users:', i
        user_id = user['id']
        count_scraped = timelinedb.count({'user.id': user_id})
        if count_scraped:
            last_tweet = timelinedb.find({'user.id':user_id}, {'id':1, 'created_at':1}).sort([('id', -1)]).limit(1)[0]  # sort: 1 = ascending, -1 = descending
            last_date = last_tweet['created_at']
            poidb.update({'id': user_id}, {'$set':{"datetime_last_timeline_scrape": last_date, 'timeline_auth_error_flag': False, "timeline_scraped_flag": True, 'timeline_count': count_scraped}}, upsert=False)

set_flag_poi_with_timeline(sample_poi, sample_time)
set_flag_poi_with_timeline(track_poi, track_time)
