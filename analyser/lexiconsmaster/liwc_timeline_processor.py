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


# set every poi to have not been analysed.
# sample_poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)
# track_poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)

'''Process the timelines of users in POI'''


def process(poi, timelines, level):
    # poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)
    poi.create_index([('timeline_count', pymongo.DESCENDING),
                      ('liwc_anal.mined', pymongo.ASCENDING),
                      ('level', pymongo.ASCENDING)])
    rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
    mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
    hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
    ugrex = re.compile(r'(https?://[^\s]+)')  # for url

    while True:
        # How many users whose timelines have not been processed by LIWC
        count = poi.count({"timeline_count": {'$gt': 0}, 'liwc_anal.mined': {'$exists': False}, 'level': {'$lte': level}})
        if count == 0:
            break
        else:
            print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + str(count) + " remaining"

        for user in poi.find({"timeline_count": {'$gt': 0}, 'liwc_anal.mined': {'$exists': False},
                              'level': {'$lte': level}}, {'id': 1}).limit(250):
            liwc = Liwc()
            textmass = ""
            for tweet in timelines.find({'user.id': user['id']}):
                # is it a retweet?
                # if not ('retweeted_status' in tweet):
                text = tweet['text'].encode('utf8')
                # replace RT, @, # and Http://
                text = rtgrex.sub('', text)
                text = mgrex.sub('', text)
                text = hgrex.sub('', text)
                text = ugrex.sub('', text)
                text = text.strip()
                if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
                    text += '.'
                textmass = textmass + " " + text.lower()
            # print ' '.join(textmass.split())
            result = Liwc.summarize_document(liwc, ' '.join(textmass.split()))
            # print result
            poi.update({'id': user['id']}, {'$set': {"liwc_anal.mined": True, "liwc_anal.result": result}}, upsert=False)
            # progcounter += 1
            # if progcounter%1000 == 0:
            #    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  + "\t" + str(progcounter)


if __name__ == '__main__':
    '''Connecting db and collections'''
    db = dbutil.db_connect_no_auth('random')
    sample_poi = db['com']
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting POI dbs well'

    sample_time = db['timeline']
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting timeline dbs well'

    '''Counting the number of users whose timelines have been processed by LIWC'''
    print 'LIWC mined user in Sample Col: ' + str(sample_poi.count({'liwc_anal.mined': {'$exists': False}}))
    process(sample_poi, sample_time, 1)

    # rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')
    # mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')
    # hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')
    # ugrex = re.compile(r'(https?://[^\s]+)')
    # text = '''RT @IAmAnaNervosa: Fatass, Go and lose some weight. https://t.co/lc98H7ANG9 RT @_cr_0sstheline_: @_cr_0sstheline_ Cross the line #fad if you're about ready #3_dfa_ to quit, but you know you can't. @faji RT @BoyAnorexic: http://t.co/lc98H7ANG9'''
    # print text
    # text = rtgrex.sub('', text)
    # print text
    # text = mgrex.sub('', text)
    # print text
    # text = hgrex.sub('', text)
    # print text
    # text = ugrex.sub('', text)
    # print text
    # print ' '.join(text.split())

