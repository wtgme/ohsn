# -*- coding: utf-8 -*-
"""
Created on 14:56, 03/11/15

@author: wt
"""

# import sys
# from os import path
# sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import db_util as dbutil
import datetime
import re
from lexicons.liwc import Liwc
import pymongo

# '''Connecting db and collections'''
db = dbutil.db_connect_no_auth('echelon')
sample_poi = db['poi']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting POI dbs well'

sample_time = db['timelines']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting timeline dbs well'

# '''Counting the number of users whose timelines have been processed by LIWC'''
print 'LIWC mined user in Sample Col: ' + str(sample_poi.find({"rliwc_anal.mined": True}).count())


# set every poi to have not been analysed.
# sample_poi.update({},{'$set':{"rliwc_anal.mined": False, "rliwc_anal.result": None}}, multi=True)
# track_poi.update({},{'$set':{"rliwc_anal.mined": False, "rliwc_anal.result": None}}, multi=True)

# '''Process the timelines of users in POI'''


def process(poi, timelines):
    poi.update({},{'$set':{"rliwc_anal.mined": False, "rliwc_anal.result": None}}, multi=True)
    poi.create_index([('timeline_auth_error_flag', pymongo.ASCENDING),
                      ('rliwc_anal.mined', pymongo.ASCENDING)])

    while True:
        # How many users whose timelines have not been processed by LIWC
        count = poi.find({'timeline_auth_error_flag':False, "rliwc_anal.mined": False}).count()
        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + str(count) + " remaining"

        for user in poi.find({'timeline_auth_error_flag':False, "rliwc_anal.mined": False}).limit(250):
            liwc = Liwc()
            textmass = ""
            for tweet in timelines.find({'user.id': user['id']}):
                # is it a retweet?
                # if not ('retweeted_status' in tweet):
                text = tweet['text'].encode('utf8')
                # text = re.sub(r"http\S+", "", text) # this doesn't do anything
                textmass = textmass + " " + text

            textmass = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", textmass).split())
            textmass.lower()
            result = Liwc.summarize_document(liwc, textmass)
            # print result

            poi.update({'id': user['id']}, {'$set': {"rliwc_anal.mined": True, "rliwc_anal.result": result}})
            # progcounter += 1
            # if progcounter%1000 == 0:
            #    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + str(progcounter)


if __name__ == '__main__':
    process(sample_poi, sample_time)
