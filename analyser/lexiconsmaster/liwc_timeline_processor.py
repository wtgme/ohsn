# -*- coding: utf-8 -*-
"""
Created on 14:56, 03/11/15

@author: wt
"""

import sys
sys.path.append('..')
import util.db_util as dbutil
import datetime
import re
from lexicons.liwc import Liwc

'''Connecting db and collections'''
db = dbutil.db_connect_no_auth('stream')
sample_poi = db['poi_sample']
track_poi = db['poi_track']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + 'Connecting POI dbs well'

sample_time = db['timeline_sample_test']
track_time = db['timeline_track_test']
print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" +  'Connecting timeline dbs well'

'''Counting the number of users whose timelines have been processed by LIWC'''
print 'LIWC mined user in Sample Col: ' + sample_poi.find({"liwc_anal.mined": True}).count()
print 'LIWC mined user in Track Col: ' + track_poi.find({"liwc_anal.mined": True}).count()


# set every poi to have not been analysed.
sample_poi.update({},{'$set':{"liwc_anal.mined": False}}, multi=True)
track_poi.update({},{'$set':{"liwc_anal.mined": False}}, multi=True)

'''Process the timelines of users in POI'''
def process(poi, timelines):
    while True:
        # How many users whose timelines have not been processed by LIWC
        count = poi.find({'timeline_auth_error_flag':False, "liwc_anal.mined": False}).count()
        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"\t"+ str(count) + " remaining"

        for user in poi.find({'timeline_auth_error_flag':False, "liwc_anal.mined": False}).limit(250):
            #progcounter += 1
            #if progcounter%1000 == 0:
            #    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + str(progcounter)
            liwc = Liwc()
            textmass = ""
            for tweet in timelines.find({'user.id': user['id']}):
            # is it a retweet?
            #if not ('retweeted_status' in tweet):
                text = tweet['text'].encode('utf8')
            # text = re.sub(r"http\S+", "", text) # this doesn't do anything
                textmass = textmass + " " + text
            # print tweet['text'].encode('utf8')

            textmass = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",textmass).split())
            textmass.lower()
            result = Liwc.summarize_document(liwc, textmass)
        #print result
        #exit()
        # Liwc.print_summarization(liwc, result)

            poi.update({'id':user['id']},{'$set':{"liwc_anal.mined": True, "liwc_anal.result":result}})


