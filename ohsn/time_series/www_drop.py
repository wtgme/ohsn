import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import pymongo
from ohsn.util import db_util as dbt
from datetime import datetime
import numpy as np
import pandas as pd
# import pickle
import cPickle as pickle
import ohsn.util.io_util as iot
from lifelines.utils import datetimes_to_durations
import ohsn.util.graph_util as gt
import scipy.stats as stats
import pymongo


def readnetwork(dbname, comname):
    # Read the subset of the who network
    com = dbt.db_connect_col(dbname, comname)
    userids = iot.get_values_one_field(dbname=dbname, colname=comname, fieldname='id', filt={'senti': {'$exists': True}})
    userids = set(userids)
    print 'length of user ids ', len(userids)
    fw = open('www.net', 'w')
    with open('/media/data/www_twitter_rv.net', 'r') as infile:
        for line in infile:
            ids = line.strip().split()
            if (int(ids[0]) in userids) and (int(ids[1]) in userids):
                fw.write(line.strip()+'\n')

    fw.flush()
    fw.close()

def get_sentiments(dbname, comname):
    com = dbt.db_connect_col(dbname, comname)
    user_sentiment = {}
    for u in com.find({'senti': {'$exists': True}}):
        uid, senti = iot.get_fields_one_doc(u, ['id', 'senti.result.whole.scalem'])
        if senti < 100:
            user_sentiment[uid] = senti
    pickle.dump(user_sentiment, open('www.sentis', 'w'))

def get_profile(dbname, comname):
    com = dbt.db_connect_col(dbname, comname)
    newcom = dbt.db_connect_col(dbname, ' newcom')
    for u in com.find({'senti': {'$exists': True}}, no_cursor_timeout=True):
        # try:
        newcom.insert(u)
        # except pymongo.errors.CursorNotFound:
        #     pass


def friends_active_days(user, f1_time):
    # print user['id']
    # ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    ts = f1_time
    try:
        tts = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    except KeyError:
        tts = ts
    delta = tts.date() - ts.date()
    days = delta.days+1
    return [days]

def user_active():
    # obtain the active duration of users in two observation
    groups = [
        ('WWW', 'www', 'com', {'level': 1, 'senti': {'$exists': True}})
    ]
    for tag, dbname, comname, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)
        first_obser = datetime.strptime('Mon Sep 28 20:03:05 +0000 2009', '%a %b %d %H:%M:%S +0000 %Y')
        network1 = gt.Graph.Read_Ncol('www.net', directed=True)
        gt.summary(network1)
        network1.vs['alive'] = 0
        network1.vs['duration'] = 0
        for v in network1.vs:
            u1 = com.find_one({'id': int(v['name'])})
        # for u1 in com.find({'senti': {'$exists': True}}):
            # v = network1.vs.find(name=str(u1['id']))
            if 'status' in u1:
                second_obser = datetime.strptime(u1['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                if second_obser > first_obser:
                    v['alive'] = 1
                    v['duration'] = friends_active_days(u1, first_obser)[0]
        network1.write_graphml(tag.lower()+'-net-all-active.graphml')

def active_days(user):
    # print user['id']
    ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    try:
        tts =  datetime.strptime('Mon Sep 28 20:03:05 +0000 2009', '%a %b %d %H:%M:%S +0000 %Y')
        # datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    except KeyError:
        tts = ts
    delta = tts.date() - ts.date()
    days = delta.days+1
    status_count = abs(float(user['statuses_count']))
    friend_count = abs(float(user['friends_count']))
    follower_count = abs(float(user['followers_count']))
    friends_day = friend_count/days
    statuses_day = status_count/days
    followers_day = follower_count/days
    return[friend_count, status_count, follower_count,
           friends_day, statuses_day, followers_day,
           days]

def friends_active_days(user, f1_time):
    # print user['id']
    # ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    ts = f1_time
    try:
        tts = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    except KeyError:
        tts = ts
    delta = tts.date() - ts.date()
    days = delta.days+1
    return [days]




def read_user_time_iv(filename):
    fields = [
            'senti'
              ]
    prof_names = ['friends_count', 'statuses_count', 'followers_count',
        'friends_day', 'statuses_day', 'followers_day', 'days']

    trimed_fields = ['-'.join(field.split('.')[-2:]) for field in fields]
    print trimed_fields
    groups = [
         ('WWW', 'www', 'com', {'senti': {'$exists': True}})
    ]

    data = []
    for tag, dbname, comname, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)

        sentims = (pickle.load(open(tag.lower() + '.sentis', 'r')))
        print len(sentims)

        network1 = gt.Graph.Read_GraphML(tag.lower()+'-net-all-active.graphml')
        gt.summary(network1)
        # network1_gc = gt.giant_component(network1)

        # network1_gc.to_undirected()
        # gt.summary(network1_gc)

        '''Centralities Calculation'''
        # eigen = network1.eigenvector_centrality()
        # pageranks = network1.pagerank()
        # indegree = network1_gc.authority_score()
        # outdegree = network1_gc.hub_score()

        # indegree = network1.coreness(mode='IN')
        # outdegree = network1.coreness(mode='ALL')

        # nodes = [int(v['name']) for v in network1.vs]
        # eigen_map = dict(zip(nodes, eigen))
        # pagerank_map = dict(zip(nodes, pageranks))

        # eigen_map = pickle.load(open('data/ed_user_retweets.pick', 'r'))
        # pagerank_map = pickle.load(open('data/ed_user_incloseness.pick', 'r'))

        # indegree_map = dict(zip(nodes, indegree))
        indegree_map = pickle.load(open('data/www_user_incore.pick', 'r'))
        # outdegree_map = dict(zip(nodes, outdegree))

        ind = pickle.load(open('data/www-indegree.pick', 'r'))
        outd = pickle.load(open('data/www-outdegree.pick', 'r'))

        frialive, friduration = {}, {}
        for v in network1.vs:
            friends = set(network1.predecessors(str(v['name'])))
            followers = set(network1.successors(str(v['name'])))
            friends = friends - followers

            if len(friends) > 0:
                falive, fduration = [], []
                for vi in friends:
                    falive.append(network1.vs[vi]['alive'])
                    fduration.append(network1.vs[vi]['duration'])
                frialive[int(v['name'])] = np.mean(falive)
                friduration[int(v['name'])] = np.mean(fduration)

        # print 'load liwc 2 batches: ' + tag.lower()+'-liwc2stage.csv'
        # liwc_df = pd.read_pickle(tag.lower()+'-liwc2stage.csv'+'.pick')


        for user in com.find(filter_values, no_cursor_timeout=True):
            first_scraped_at = datetime.strptime('Mon Sep 28 20:03:05 +0000 2009', '%a %b %d %H:%M:%S +0000 %Y')
            if 'status' in user:
                uid = user['id']
                last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                drop = 1
                if first_scraped_at < last_post :
                    drop = 0
                    survival = friends_active_days(user, first_scraped_at)[0]


                created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

                u_timeline_count = user['timeline_count']

                # values = iot.get_fields_one_doc(user, fields)
                values = [sentims[uid], ind[uid], outd[uid]]
                level = user['level']


                # u_centrality = eigen_map.get(user['id'], 0)
                # u_pagerank = pagerank_map.get(user['id'], 0)
                u_indegree = indegree_map.get(user['id'], 0)
                # u_outdegree = outdegree_map.get(user['id'], 0)

                # values.extend(liwc_changes)
                values.extend(active_days(user))

                '''Get friends' profiles'''
                exist = True
                try:
                    v = network1.vs.find(name=str(uid))
                except ValueError:
                    exist = False
                if exist:
                    neighbors = set(network1.neighbors(str(uid))) # id or name
                    friends = set(network1.predecessors(str(uid)))
                    allfollowees = friends
                    followers = set(network1.successors(str(uid)))
                    friends = friends - followers
                    if len(friends) > 0:
                        friend_ids = [int(network1.vs[vi]['name']) for vi in friends] # return id
                        print uid in friend_ids
                        print len(friend_ids)
                        fatts = []
                        alive = 0
                        fatts_dis = []
                        ffatts = []

                        for fid in friend_ids:
                            if fid in sentims:
                                fatt  = [sentims[fid]]
                                fatt.extend([
                                    # eigen_map.get(fid, 0), pagerank_map.get(fid, 0),
                                             indegree_map.get(fid, 0)])
                                fatts.append(fatt)

                        # emotional distance
                        # friend_ids = [int(network1.vs[vi]['name']) for vi in allfollowees] # all followings for distance calculation
                        for fid in friend_ids:
                            if fid in sentims:
                                fatt_dis = [sentims[fid]]
                                # fatt_dis = [(sentims[uid] - sentims[fid])*(sentims[uid] - sentims[fid])]
                                fatts_dis.append(fatt_dis)

                                # friends' friends' distance
                                friendfriends = set(network1.predecessors(str(fid))) # all followings' followings as IV for distance
                                # followerfollowers = set(network1.predecessors(str(fid)))
                                friendfriends = friendfriends - neighbors
                                if len(friendfriends) > 0:
                                    friendfriends_ids = [int(network1.vs[vi]['name']) for vi in friendfriends] # return id
                                    for ffid in friendfriends_ids:
                                        if ffid in sentims:
                                            ffatt = [sentims[ffid]]
                                            # ffatt = [(sentims[uid] - sentims[ffid])*(sentims[uid] - sentims[ffid])]
                                            ffatts.append(ffatt)


                        if (len(fatts) > 0) and (len(ffatts)>0):
                            fatts = np.array(fatts)
                            fmatts = np.mean(fatts, axis=0)

                            fatts_dis = np.array(fatts_dis)
                            fmatts_dis = np.mean(fatts_dis, axis=0)

                            ffatts = np.array(ffatts)
                            ffmatts = np.mean(ffatts, axis=0)

                            values.extend(fmatts)
                            values.extend(fmatts_dis)
                            # paliv = float(alive)/len(fatts)
                            paliv = frialive.get(uid)
                            fdays = friduration.get(uid)
                            data.append([user['id_str'], level, drop, survival, created_at, last_post,
                                         first_scraped_at, tag,
                                         u_indegree, u_timeline_count] +
                                        values + [len(fatts), paliv, fdays]
                                        + ffmatts.tolist())

    df = pd.DataFrame(data, columns=['uid', 'level', 'dropout', 'survival', 'created_at', 'last_post', 'first_scraped_at',
                                     'group','u_incore',
                                     'u_timeline_count'] +
                                    ['u_'+field for field in trimed_fields] +
                                    ['u_ind', 'u_outd'] +
                                    # ['u_prior_'+field for field in trimed_fields] +
                                    # ['u_post_'+field for field in trimed_fields] +
                                    # ['u_change_'+field for field in trimed_fields] +
                                    ['u_'+field for field in prof_names] +
                                    ['f_'+tf for tf in trimed_fields]  +
                                    ['f_incore'] +
                                    ['f_avg_'+tf for tf in trimed_fields]  +
                                    ['f_num', 'f_palive', 'f_days']
                                    + ['ff_avg_'+field for field in trimed_fields] )
    df.to_csv(filename)

def www_in_out_degree():
    ind, outd = {}, {}
    with open('/media/data/www_twitter_rv.net', 'r') as infile:
        for line in infile:
            ids = line.strip().split()
            user = int(ids[0])
            follower = int(ids[1])
            ind[user] = ind.get(user, 0) + 1
            outd[follower] = outd.get(follower, 0) + 1
    pickle.dump(ind, open('data/www-indegree.pick', 'w'))
    pickle.dump(outd, open('data/www-outdegree.pick', 'w'))

if __name__ == '__main__':
    # readnetwork('www', 'com')
    # get_sentiments('www', 'com')
    # get_profile('www', 'com')
    # user_active()
    read_user_time_iv('www-user-durations-iv-following-senti.csv')
    # www_in_out_degree()