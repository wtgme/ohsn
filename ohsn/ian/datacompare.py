# -*- coding: utf-8 -*-
"""
Created on 14:30, 17/10/17

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import ohsn.util.graph_util as gt
import pymongo
import ohsn.api.profiles_check as pck
import datetime
import ohsn.textprocessor.description_miner as dm
import pandas as pd
import re
import sys
from ohsn.lexiconsmaster.lexicons.liwc import Liwc
import pymongo
import pickle
from ohsn.api import timelines


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

# def filter_user():
#     # filter ED users from Ian data
#     conn = dbt.db_connect_no_auth_ian()
#     iandb = conn.connect('TwitterProAna')
#     ianusers = iandb['users']
#     for u in ianusers.find({}, no_cursor_timeout=True):
#         if 'description' in u:
#             text = u['description']
#             if text != None and pck.check_ed_profile(text):
#                 print u['id']
#         else:
#             if 'history' in u:
#                 hists = u['history']
#                 for h in hists:
#                     if 'description' in h:
#                         text = h['description']
#                         if text != None and pck.check_ed_profile(text):
#                             print u['id']
#     conn.disconnect()


def overlap():
    # overlap between two data
    core_ed = set(iot.get_values_one_field('fed', 'scom', 'id'))
    ian_ed = set()
    with open('uid.txt', 'r') as fo:
        for line in fo.readlines():
            ian_ed.add(int(line.strip()))
    print len(core_ed), len(ian_ed), len(core_ed.intersection(ian_ed))

    fed = set(iot.get_values_one_field('fed', 'com', 'id'))
    ian_all = set(iot.get_values_one_field('TwitterProAna', 'users', 'id'))
    print len(fed), len(ian_all), len(fed.intersection(ian_all))
    print len(fed), len(ian_ed), len(fed.intersection(ian_ed))


# def data_transform():
#     # transform data from ian db to local db
#     conn = dbt.db_connect_no_auth_ian()
#     iandb = conn.connect('TwitterProAna')
#     ianusers = iandb['users']
#     users = dbt.db_connect_col('TwitterProAna', 'users')
#     users.create_index([('id', pymongo.ASCENDING)], unique=True)

#     for u in ianusers.find({}, no_cursor_timeout=True):
#         try:
#             users.insert(u)
#         except pymongo.errors.DuplicateKeyError:
#             pass

#     ianusers = iandb['tweets']
#     users = dbt.db_connect_col('TwitterProAna', 'tweets')
#     users.create_index([('user.id', pymongo.ASCENDING),
#                           ('id', pymongo.DESCENDING)])
#     users.create_index([('id', pymongo.ASCENDING)], unique=True)

#     for u in ianusers.find({}, no_cursor_timeout=True):
#         try:
#             users.insert(u)
#         except pymongo.errors.DuplicateKeyError:
#             pass
#     conn.disconnect()


def tweet_stat():
    # stats tweeting activity over time
    tweets = dbt.db_connect_col('TwitterProAna', 'tweets')
    print ('%s\t%s\t%s') %('tid', 'uid', 'date')
    for tweet in tweets.find({}, no_cursor_timeout=True):
        print ('%s\t%s\t%s') %('t'+str(tweet['id']), 'u'+str(tweet['from_user_id']), tweet['created_at'])


def follow_net(dbname, collection):
    # recover follow network among users
    com = dbt.db_connect_col(dbname, collection)
    for row in com.find({'screen_name': {'$exists': True}}, no_cursor_timeout=True):
        ego = str(row['id'])
        if 'followData' in row:
            friends = row['followData']
            # if ('friends' in friends) and ('followers' in friends):
            #     print ego, len(set(friends['friends']).
            #                    intersection(set(friends['followers'])))

            if 'friends' in friends:
                for followee in friends['friends']:
                    print ego + '\t' + str(followee)
            if 'followers' in friends:
                for follower in friends['followers']:
                    print str(follower) + '\t' + ego

    # name_map, edges = {}, set()
    # with open('net.txt', 'r') as fo:
    #     for line in fo.readlines():
    #         n1, n2 = line.split('\t')
    #         n1id = name_map.get(n1, len(name_map))
    #         name_map[n1] = n1id
    #         n2id = name_map.get(n2, len(name_map))
    #         name_map[n2] = n2id
    #         edges.add((n1id, n2id))
    # g = gt.Graph(len(name_map), directed=True)
    # g.vs["name"] = list(sorted(name_map, key=name_map.get))
    # g.add_edges(list(edges))
    # g.es["weight"] = 1
    # g.write_graphml('follow.graphml')


def hashtag_net(dbname, colname):
    # built hashtag_net
    g = gt.load_hashtag_coocurrent_network_undir(dbname, colname)
    g.write_graphml('tag.graphml')


def hot_day(filename, dbname='TwitterProAna', colname='tweets'):
    df = pd.read_csv(filename, sep='\t')
    df['date']  = pd.DatetimeIndex(df.date).normalize()
    # print df
    mask = (df['date'] == '2013-03-27')
    df = df.loc[mask]
    tweets = dbt.db_connect_col(dbname, colname)
    tids = []
    for tid in df['tid']:
        tid = tid.replace('t', '')
        tids.append(int(tid))
    # print tids
    for tweet in tweets.find({'id': {'$in': tids}}):
        print str(tweet['id']), tweet['text'].encode('utf-8')


def bio_information(dbname='TwitterProAna', colname='users'):
    com = dbt.db_connect_col(dbname, colname)
    bio_hist = dbt.db_connect_col(dbname, 'bio')
    bio_hist.create_index([('id', pymongo.ASCENDING)])


    for row in com.find({'screen_name': {'$exists': True}}, no_cursor_timeout=True):
        name, text = row['name'], row['description']
        date = row['lastPolledFull']
        if text and name:
            stats = dm.process_text(text, name)
        elif text:
            stats = dm.process_text(text)
        if stats:
            stats['date'] = date
            stats['id'] = row['id']
            try:
                bio_hist.insert(stats)
            except pymongo.errors.DuplicateKeyError:
                pass
        for hist in reversed(row['history']):
            if 'name' in hist:
                name = hist['name']
            if 'description' in hist:
                text = hist['description']
                if text:
                    stats = dm.process_text(text, name)
                    if stats:
                        stats['date'] = hist['lastPolledFull']
                        stats['id'] = row['id']
                        try:
                            bio_hist.insert(stats)
                        except pymongo.errors.DuplicateKeyError:
                            pass

def bio_change(dbname='TwitterProAna', colname='bio', field='cbmi'):
    data = []
    bio = dbt.db_connect_col(dbname, colname)
    for entry in bio.find({field:{'$exists':True}}):
        data.append([entry['id'], entry['date'], entry[field]['value']])
    df = pd.DataFrame(data=data, columns=['uid', 'date', field])
    df.to_csv('ian-'+field+'.csv')


def geo_infor(dbname='TwitterProAna', colname='tweets'):
    # Twitter represents it as a latitude then a longitude: "geo": { "type":"Point", "coordinates":[37.78217, -122.40062] }
    data = []
    tweets = dbt.db_connect_col(dbname, colname)
    for tweet in tweets.find({'geo':{'$ne':None}}, no_cursor_timeout=True):
        lat, long = tweet['geo']['coordinates']
        tid = str(tweet['id'])
        uid = str(tweet['from_user_id'])
        date = tweet['created_at']
        data.append([tid, uid, lat, long, date])
    df = pd.DataFrame(data=data, columns=['tid', 'uid', 'lat', 'long', 'date'])
    df.to_csv('ian-geo.csv')


def data_split(dbname='TwitterProAna', colname='tweets'):
    # # https://stackoverflow.com/questions/8136652/query-mongodb-on-month-day-year-of-a-datetime
    # # Label tweets with dates
    # tweets = dbt.db_connect_col(dbname, colname)
    # # basedate = datetime(1970, 1, 1)
    # # tweets.create_index([('date_week', pymongo.ASCENDING)])
    # # for tweet in tweets.find({}, no_cursor_timeout=True):
    # #     creat = tweet['created_at']
    # #     detal = creat - basedate
    # #     datestr = detal.days // 7 + 1
    # #     tweets.update_one({'id': tweet['id']}, {'$set': {"date_week": datestr}}, upsert=False)
    #
    # # # Indexing tweets with dates
    # date_index = {}
    # for tweet in tweets.find({}, ['id', 'date_week'], no_cursor_timeout=True):
    #     tid, date = tweet['id'], tweet['date_week']
    #     tlist = date_index.get(date, [])
    #     tlist.append(tid)
    #     date_index[date] = tlist
    # pickle.dump(date_index, open('date_tid_list_week.pick', 'w'))
    #
    # # Bunch with tweets in give dates to produce LIWC results
    # # tweets = dbt.db_connect_col(dbname, colname)
    # # date_index = pickle.load(open('date_tid_list_week.pick', 'r'))
    # timeseries = dbt.db_connect_col(dbname, 'weekseries')
    # for key in date_index.keys():
    #     tlist = date_index[key]
    #     textmass = ''
    #     for tid in tlist:
    #         tweet = tweets.find_one({'id': tid})
    #         text = tweet['text'].encode('utf8')
    #         # replace RT, @, # and Http://
    #         match = rtgrex.search(text)
    #         if match is None:
    #             text = mgrex.sub('', text)
    #             text = hgrex.sub('', text)
    #             text = ugrex.sub('', text)
    #             text = text.strip()
    #             if not(text.endswith('.') or text.endswith('?') or text.endswith('!')):
    #                 text += '.'
    #             textmass += " " + text.lower()
    #     words = textmass.split()
    #     # Any text with fewer than 50 words should be looked at with a certain degree of skepticism.
    #     if len(words) > 50:
    #         liwc_result = liwc.summarize_document(' '.join(words))
    #         timeseries.insert({'date': key, 'liwc':liwc_result})

    timeseries = dbt.db_connect_col(dbname, 'weekseries')
    fields = iot.read_fields()
    fields_trim = [f.replace('liwc_anal.result.', '') for f in fields]
    fields = [f.replace('_anal.result', '') for f in fields]

    print len(fields)
    data = []
    basedate = datetime(1970, 1, 1)
    for entry in timeseries.find():
        time = entry['date']
        # date = datetime.strptime(time, '%Y-%m')
        # date = datetime.date(year=int(time[0]), month=int(time[1]))
        # detal = creat - basedate
    # #     datestr = detal.days // 7 + 1
        days = (time -1)*7
        date = basedate + datetime.timedelta(days=days)
        features = iot.get_fields_one_doc(entry, fields)
        data.append([date] + features)
    df = pd.DataFrame(data=data, columns=['date'] + fields_trim)
    df.to_csv('ian-liwc-tweets-week.csv')

def timeline(dbname, comname, timename, streamname):
    # return users' timelines from a time to a time
    stream = dbt.db_connect_col(dbname, streamname)
    most_recenty = stream.find().sort([('id', -1)]).limit(1)
    oldest = stream.find().sort([('id', 1)]).limit(1)
    max_id = most_recenty[0]['id']
    since_id = oldest[0]['id']
    print most_recenty[0]
    print oldest[0]
    com = dbt.db_connect_col(dbname, comname)
    timeline = dbt.db_connect_col(dbname, timename)

    com.create_index([('timeline_scraped_times', pymongo.ASCENDING)])
    timeline.create_index([('user.id', pymongo.ASCENDING),
                          ('id', pymongo.DESCENDING)])
    timeline.create_index([('id', pymongo.ASCENDING)], unique=True)

    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "\t" + 'Connect Twitter.com'
    timelines.retrieve_timeline(com, timeline, max_id)
    print datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'finish timeline for sample users'

def bio_all_in_line(dbname='TwitterProAna', colname='bio'):
    names = ['cbmi', 'gbmi', 'a', 'gender', 'h', 'cw', 'gw', 'lw', 'hw', 'ugw']
    fields = ['id','date'] + [name+'.value' for name in names]
    data = []
    bio = dbt.db_connect_col(dbname, colname)
    for entry in bio.find({}):
        dat = (iot.get_fields_one_doc(entry, fields))
        if set(dat[3:]) != set([0.0]):
            data.append(dat)
    df = pd.DataFrame(data=data, columns=['id','date'] +names)
    df.to_csv('ian-all'+'.csv')

if __name__ == '__main__':
    # filter_user()
    # overlap()

    # data_transform()
    # tweet_stat()
    # follow_net('TwitterProAna', 'users')
    # hashtag_net('TwitterProAna', 'tweets')
    # hot_day('tweets.csv')
    # bio_information()
    # for f in ['cbmi', 'gbmi', 'a', 'gender', 'h', 'cw', 'gw', 'lw', 'hw', 'ugw']:
    #     bio_change(dbname='TwitterProAna', colname='bio', field=f)
    # geo_infor()
    # data_split()
    # timeline('TwitterProAna', 'users', 'timeline', 'tweets')
    bio_all_in_line()