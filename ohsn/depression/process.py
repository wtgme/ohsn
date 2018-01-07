# -*- coding: utf-8 -*-
"""
Created on 14:33, 20/04/17

@author: wt

Data:
Here’s depression users’ tweet dataset, https://drive.google.com/open?id=0B2bd0yejz160TE5ORTIzdTA1M1k .
We combined depressive users extracted from the dataset you sent to us and our own dataset.
There’re three files in the shared folder:
—timeline2.json (6,784,273 tweets with 8,031 users, all tweets information)
—users1.json (7,652 users, user profile information extracted from your dataset — com file)
—users2.json (379 users, user profile information extracted from our dataset)
(For discrimination, two parts of users are not combined because some attributes are not the same between the two datasets.)
These files can be imported directly into MongoDB.

Aims:
hen, you can re-construct the contents similar to the Section 5, Section 6.4, and Section 6.5 of your WSDM paper by using our Depression data set instead of the ED data set.
That way, hopefully the workload won't be too much to you.
As there is more space in a journal paper, you may also add more necessary details and descriptions to these Sub-sections.
Also, since MISQ does not accept Latex, you can simply put all the contents in a MS Word document.

LIWC variables: depression data include retweets
imported users2 into com and timeline2 into timeline

"""

import json
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import pymongo
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
from os import listdir
from os.path import isfile, join
import ast
import ohsn.util.graph_util as gt
import numpy as np


def store_users_profile(dbname='depression', colname='neg_com', filepath='/home/wt/Code/ohsn/ohsn/depression/data/negative/user_profile/written_users_info_detail_list.txt'):
    # import with mongodb tool
    com = dbt.db_connect_col(dbname, colname)
    com.create_index("id", unique=True)

    with open(filepath) as data_file:
        for line in data_file.readlines():
            print line
            parsed_json = ast.literal_eval(line.strip())
            try:
                com.insert(parsed_json)
            except pymongo.errors.DuplicateKeyError:
                    pass

def store_tweets(dbname='depression', colname='neg_timeline', mypath='/home/wt/Code/ohsn/ohsn/depression/data/negative/user_tweets'):
    times = dbt.db_connect_col('depression', 'neg_timeline')
    times.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    times.create_index([('id', pymongo.ASCENDING)], unique=True)

    # mypath = '/home/wt/Code/ohsn/ohsn/depression/data/negative/user_tweets'
    onlyfiles = [mypath+'/'+f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file_path in onlyfiles:
        with open(file_path) as data_file:
            print file_path
            for line in data_file.readlines():
                parsed_json = ast.literal_eval(line.strip())
                try:
                    times.insert(parsed_json)
                except pymongo.errors.DuplicateKeyError:
                    pass

def trandb(dbname, colnam1, colnam2):
    time1 = dbt.db_connect_col(dbname, colnam1)
    time2 = dbt.db_connect_col(dbname, colnam2)
    for t in time2.find():
        try:
            time1.insert(t)
        except pymongo.errors.DuplicateKeyError:
            pass

def label_positive():
    com = dbt.db_connect_col('depression', 'com')
    with open('/home/wt/Code/ohsn/ohsn/depression/data/positive/positive_users_selections_screennaes.txt') as data_file:
        for line in data_file.readlines():
            print line
            screen_name = line.strip()
            com.update_one({'screen_name': screen_name}, {'$set': {'checked': True}}, upsert=False)

def data_stat():
    # stat for how many users
    stream = dbt.db_connect_col('depression', 'search')
    uids = set()
    for tweet in stream.find({}):
        uids.add(tweet['user']['id'])
    print len(uids)


def network_analysis():
    # output network among depression users
    # user1 = iot.get_values_one_field('depression', 'users1', 'id')
    # user2 = iot.get_values_one_field('depression', 'users2', 'id')
    # print len(user1), len(user2)
    # alluser = user1 + user2
    alluser = iot.get_values_one_field('depression', 'depressive', 'id')
    follow_net = gt.load_network_subset('depression', 'net', {'user': {'$in': alluser},
                                                              'follower': {'$in': alluser}})
    gt.net_stat(follow_net)
    follow_net.write_graphml('data/follow_net.graphml')

    for beh in ['retweet', 'communication']:
        print beh
        bnetwork = gt.load_beh_network_subset(userlist=alluser, db_name='depression',
                                              collection='bnet', btype=beh)
        gt.net_stat(bnetwork)
        bnetwork.write_graphml('data/'+beh+'_net.graphml')


def liwc_feature():
    fields = iot.read_fields()
    for field in fields:
        values = iot.get_values_one_field('depression', 'users1', field)
        print field, np.mean(values), np.std(values)


def drop_initials(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i > -1000000000.0]


def network_assort():
    # test network assortative
    gs = ['edfollow','follow', 'retweet', 'communication']
    fields = iot.read_fields()
    print len(fields)
    for gf in gs[1:]:
        g = gt.Graph.Read_GraphML('data/'+gf+'_net.graphml')
        # g = gt.giant_component(g)
        gt.net_stat(g)

        for filed in fields:
            g = gt.add_attribute(g, 'foi', 'depression', 'com', filed)
            raw_values = np.array(g.vs['foi'])
            values = drop_initials(raw_values)
            if len(values) > 100:
                output = gf + ',' + filed.split('.')[-1] + ','
                # maxv, minv = np.percentile(values, 97.5), np.percentile(values, 2.5)
                maxv, minv = max(values), min(values)
                vs = g.vs.select(foi_ge=minv, foi_le=maxv)
                sg = g.subgraph(vs)
                raw_assort = sg.assortativity('foi', 'foi', directed=True)
                ass_list = []
                for i in xrange(1000):
                    np.random.shuffle(raw_values)
                    g.vs["foi"] = raw_values
                    vs = g.vs.select(foi_ge=minv, foi_le=maxv)
                    sg = g.subgraph(vs)
                    ass_list.append(sg.assortativity('foi', 'foi', directed=True))

                ass_list = np.array(ass_list)
                amean, astd = np.mean(ass_list), np.std(ass_list)
                absobserved = abs(raw_assort)
                pval = (np.sum(ass_list >= absobserved) +
                        np.sum(ass_list <= -absobserved))/float(len(ass_list))
                zscore = (raw_assort-amean)/astd
                output += format(raw_assort, '.2f') + ',' + format(amean, '.2f') + ',' + \
                          format(astd, '.2f') + ',' + format(zscore, '.2f') + ',' + format(pval, '.2f')
                if pval < 0.001:
                    output += '***'
                    print output
                    continue
                if pval < 0.01:
                    output += '**'
                    print output
                    continue
                if pval < 0.05:
                    output += '*'
                    print output
                    continue
                else:
                    print output
                    continue

def user_cluster(filepath='data/depression.data'):
    from sklearn.datasets import load_svmlight_file
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    import pandas as pd
    import ohsn.util.plot_util as plu
    from sklearn import preprocessing
    import seaborn as sns
    import matplotlib.pyplot as plt


    X, y = load_svmlight_file(filepath, multilabel=False)
    X = X.toarray()
    min_max_scaler = preprocessing.MinMaxScaler()
    X = min_max_scaler.fit_transform(X)
    # X = preprocessing.scale(X)
    print X.shape
    #
    # range_n_clusters = range(2, 21)
    # data = []
    # for n_clusters in range_n_clusters:
    #     for i in range(10):
    #         clusterer = KMeans(n_clusters=n_clusters, n_jobs=8)
    #         cluster_labels = clusterer.fit_predict(X)
    #         silhouette_avg = silhouette_score(X, cluster_labels)
    #         print("For n_clusters =", n_clusters, "The average silhouette_score is :", silhouette_avg)
    #         data.append([n_clusters, silhouette_avg])
    # df = pd.DataFrame(data, columns=['cluster', 'silhouette_avg'])
    # df.to_csv('depress-user-kmeans.csv')

    # df = pd.read_csv('depress-user-kmeans.csv', index_col=0)
    #
    # plu.plot_config()
    # sns.boxplot(x="cluster", y="silhouette_avg", data=df, color="#af8dc3")
    # sns.despine(offset=10, trim=True)
    # plt.xlabel('K')
    # plt.ylabel('Average Silhouette')
    # # plu.ylim(0.38, 0.81)
    # plt.show()



    clusterer = KMeans(n_clusters=2, n_jobs=8)
    cluster_labels = clusterer.fit_predict(X)
    ids = []
    with open(filepath, 'r') as fo:
        for line in fo.readlines():
            tokens = line.split(' ')
            ids.append(tokens[0])
    dictionary = dict(zip(ids, cluster_labels))
    gs = ['follow', 'retweet', 'communication']
    for gf in gs:
        g = gt.Graph.Read_GraphML('data/'+gf+'_net.graphml')
        for v in g.vs:
            v['cluster'] = dictionary.get(v['name'], -1)
        g.write_graphml('data/'+gf+'_net_cluster.graphml')



if __name__ == '__main__':
    # store_users_profile()
    # store_users_profile('depression', 'therapist', '/home/wt/Code/ohsn/ohsn/depression/data/relabel/users_therapist.json')
    # store_tweets()
    # label_positive()

    # data_stat()
    # network_analysis()
    # trandb('depression', 'timeline', 'timeline2')
    # g = gt.load_network('fed', 'snet')
    # g.write_graphml('data/' + 'edfollow'+'_net.graphml')
    network_assort()
    # liwc_feature()
    # user_cluster()