# -*- coding: utf-8 -*-
"""
Created on 14:56, 03/11/15

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbutil
import datetime
import re
import sys
from ohsn.lexiconsmaster.lexicons.liwc import Liwc
import pymongo


# set every poi to have not been analysed.
# sample_poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)
# track_poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)

'''Process the timelines of users in POI'''
rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
# hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
ugrex = re.compile(r'(https?://[^\s]+)')  # for url
liwc = Liwc()


def process_tweet(tweets, Trim_rt=True):
    '''Input: a list of tweet text
       Output: the LIWC results in terms of these tweets
    '''
    textmass = ""
    for tweet in tweets:
        if Trim_rt and 'retweeted_status' in tweet:
            continue
        elif Trim_rt and 'quoted_status' in tweet:
            continue
        else:
            text = tweet['text'].encode('utf8')
            # replace RT, @, # and Http://
            text = rtgrex.sub('', text)
            text = mgrex.sub('', text)
            text = hgrex.sub('', text)
            text = ugrex.sub('', text)
            text = text.strip()
            if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
                text += '.'
            textmass += " " + text.lower()
    words = textmass.split()
    # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
    if len(words) > 50:
        liwc_result = liwc.summarize_document(' '.join(words))
        return liwc_result
    else:
        return None


def process(poi, timelines, fieldname, level):
    print 'Process LIWC'
    target = fieldname + '.mined'
    result = fieldname + '.result'
    # poi.update({},{'$set':{"liwc_anal.mined": False, "liwc_anal.result": None}}, multi=True)
    poi.create_index([
        # ('timeline_count', pymongo.DESCENDING),
                      (target, pymongo.ASCENDING),
                      # ('level', pymongo.ASCENDING)
    ])

    from_date = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    to_date = datetime.datetime(2021, 1, 1, 0, 0, 0, 0)


    while True:
        # How many users whose timelines have not been processed by LIWC
        finded = poi.find_one({
            "timeline_count": {'$gt': 0},
            target: {'$exists': False},
            # 'level': {'$lte': level}
            })
        # print finded
        if finded is None:
            break
        # else:
        #     print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t"+ " remaining"

        for user in poi.find({
            "timeline_count": {'$gt': 0},
            target: {'$exists': False},
                              # 'level': {'$lte': level}
        }, {'id': 1}).limit(250):
            # print user['id']
            textmass = ""

            for tweet in timelines.find({'user.id': user['id'], 'created_at': {'$gte': from_date, '$lt': to_date}}):
                if 'retweeted_status' in tweet:
                    continue
                elif 'quoted_status' in tweet:
                    continue
                else:
                    text = tweet['text'].encode('utf8')
                    # replace RT, @, # and Http://
                    text = rtgrex.sub('', text)
                    text = mgrex.sub('', text)
                    text = hgrex.sub('', text)
                    text = ugrex.sub('', text)
                    text = text.strip()
                    if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
                        text += '.'
                    textmass += " " + text.lower()
            words = textmass.split()
            # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
            if len(words) > 50:
                liwc_result = liwc.summarize_document(' '.join(words))
                poi.update_one({'id': user['id']}, {'$set': {target: True, result: liwc_result}}, upsert=False)
            else:
                poi.update_one({'id': user['id']}, {'$set': {target: True, result: None}}, upsert=False)


def process_db(dbname, colname, timename, fieldname):
    '''Connecting db and collections'''
    db = dbutil.db_connect_no_auth(dbname)
    sample_poi = db[colname]
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting POI dbs well', dbname, colname

    sample_time = db[timename]
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connecting timeline dbs well'

    '''Counting the number of users whose timelines have been processed by LIWC'''
    # print 'LIWC mined user in Sample Col: ' + str(sample_poi.count({fieldname+'.mined': {'$exists': False}}))
    process(sample_poi, sample_time, fieldname, 1000)

if __name__ == '__main__':
    # process_db('www', 'newcom', 'timeline', 'liwc_anal')
    # process_db('covid', 'geo_user_2020', 'geo_user_2020_timeline', 'liwc_anal')
    process_db('covid', 'geo_user_2020', 'geo_user_2020_timeline', 'liwc_anal_2020')

    # process_db('fed', 'pro_mention_miss_com', 'pro_mention_miss_timeline', 'liwc_anal')
    # process_db('TwitterProAna', 'users', 'timeline', 'liwc_anal')
    # process_db('depression', 'neg_com', 'neg_timeline', 'liwc_anal')
    # process_db('random', 'com', 'timeline', 'liwc_anal')
    # process_db('younger', 'com', 'timeline', 'liwc_anal')
    # process_db('fed2', 'com', 'timeline', 'liwc_anal')
    # process_db('fed3', 'com', 'timeline', 'liwc_anal')
    # process_db('fed4', 'com', 'timeline', 'liwc_anal')
    # print sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    # process_db(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    # process_db('random', 'com', 'timeline')
    # process_db('young', 'com', 'timeline')
    # process_db('sed', 'com', 'timeline')
    # process_db('srd', 'com', 'timeline')
    # process_db('syg', 'com', 'timeline')

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
    # test = 'fadfji aji  jaojf asfdj. ajfoia, fjaial aja.'
    # print test.split()


    # '''test one user'''
    # timelines = dbutil.db_connect_col('depression', 'timeline')   # depression data include retweets
    # textmass = ''
    # for tweet in timelines.find({'user.id': 1618347925}):
    #     if 'retweeted_status' in tweet:
    #         continue
    #     elif 'quoted_status' in tweet:
    #         continue
    #     else:
    #         text = tweet['text'].encode('utf8')
    #         # replace RT, @, # and Http://
    #         text = rtgrex.sub('', text)
    #         text = mgrex.sub('', text)
    #         text = hgrex.sub('', text)
    #         text = ugrex.sub('', text)
    #         text = text.strip()
    #         if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
    #             text += '.'
    #         textmass += " " + text.lower()
    # words = textmass.split()
    # # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
    # if len(words) > 50:
    #     liwc_result = liwc.summarize_document(' '.join(words))
    #     print liwc_result



# Fed data excluded retweets
# Fed2 data excluded retweets
# Fed3 data excluded retweets
# Fed4 data excluded retweets
# Random date excluded retweets