# -*- coding: utf-8 -*-
"""
Created on 14:56, 03/11/15

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbutil
import datetime
import re
from lexicons.liwc import Liwc
import pymongo

'''Connecting db and collections'''
db = dbutil.db_connect_no_auth('stream')
sample_poi = db['poi_sample']
track_poi = db['poi_track']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting POI dbs well'

sample_time = db['timeline_sample']
track_time = db['timeline_track']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting timeline dbs well'

'''Counting the number of users whose timelines have been processed by LIWC'''
print 'LIWC mined user in Sample Col: ' + str(sample_poi.count({'liwc_anal.mined': {'$exists': False}}))
print 'LIWC mined user in Track Col: ' + str(track_poi.count({'liwc_anal.mined': {'$exists': False}}))


# set every poi to have not been analysed.
# sample_poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)
# track_poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)

'''Process the timelines of users in POI'''


def process(poi, timelines, level):
    # poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)
    poi.create_index([('timeline_count', pymongo.DESCENDING),
                      ('liwc_anal.mined', pymongo.ASCENDING),
                      ('level', pymongo.ASCENDING)])

    while True:
        # How many users whose timelines have not been processed by LIWC
        count = poi.count({"timeline_count": {'$gt': 0}, 'liwc_anal.mined': {'$exists': False}, 'level': {'$lte': level}})
        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + str(count) + " remaining"

        for user in poi.find({"timeline_count": {'$gt': 0}, 'liwc_anal.mined': {'$exists': False}, 'level': {'$lte': level}}, {'id': 1}).limit(250):
            liwc = Liwc()
            textmass = ""
            for tweet in timelines.find({'user.id': user['id']}):
                # is it a retweet?
                # if not ('retweeted_status' in tweet):
                text = tweet['text'].encode('utf8')
                # text = re.sub(r"http\S+", "", text) # this doesn't do anything
                textmass = textmass + " " + text

            # textmass = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", textmass).split())
            textmass = ' '.join(re.sub("(@[A-Za-z0-9]+)|(\w+:\/\/\S+)", " ", textmass).split())
            textmass.lower()
            result = Liwc.summarize_document(liwc, textmass)
            # print result

            poi.update({'id': user['id']}, {'$set': {"liwc_anal.mined": True, "liwc_anal.result": result}}, upsert=False)
            # progcounter += 1
            # if progcounter%1000 == 0:
            #    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + str(progcounter)


if __name__ == '__main__':
    # process(sample_poi, sample_time, 2)
    process(track_poi, track_time, 2)
