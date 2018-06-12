# -*- coding: utf-8 -*-
"""
Created on 10:51, 06/06/17

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.graph_util as gt
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pandas as pd
import numpy as np
import pickle
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import ohsn.util.plot_util as plu
from sklearn.datasets import load_svmlight_file
from sklearn.metrics.pairwise import cosine_similarity
from sklearn import preprocessing
import ohsn.util.statis_util as statu
import statsmodels.api as sm
from scipy.stats import ttest_ind
import ohsn.sentiment.senstrength as sentre
import re
import statsmodels.stats.api as sms
import powerlaw
import scipy
from statsmodels.formula.api import logit
# import scikits.bootstrap as bootstrap

rtgrex = re.compile(r'RT (?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+):')  # for Retweet
mgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')  # for mention
hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9]))#([A-Za-z0-9_]+)')  # for hashtags
# hgrex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)')  # for hashtags
ugrex = re.compile(r'(https?://[^\s]+)')  # for url

def net_attr(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''network statistics'''
    user_net = gt.Graph.Read_GraphML(filename)

    cluster1 = user_net.subgraph(user_net.vs(cluster=0))
    cluster2 = user_net.subgraph(user_net.vs(cluster=1))
    gt.summary(user_net)
    gt.net_stat(user_net)
    gt.net_stat(cluster1)
    gt.net_stat(cluster2)


def prelevence():
    # counting how popular each type of content overall
    # prelence.pick for all tweets and retweets
    # tweet-prelence.pick only counting tweets to avoid duplicated counting
    # this should only use tweet, avoiding duplicated counting. https://twittercommunity.com/t/is-the-retweet-count-for-a-tweet-object-correct-when-it-is-a-retweet/8751/2
    ped = set(iot.read_ed_pro_hashtags())
    pre = set(iot.read_ed_recovery_hashtags())
    times = dbt.db_connect_col('fed', 'ed_tag')
    data = []
    for tweet in times.find({}, no_cursor_timeout=True):
        if 'retweeted_status' in tweet:
            continue
        elif 'quoted_status' in tweet:
            continue
        else:
            hashtags = tweet['entities']['hashtags']
            hash_set = set()
            for hash in hashtags:
                hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
            pred_sub = hash_set.intersection(ped)
            prec_sub = hash_set.intersection(pre)
            if pred_sub and (len(prec_sub) == 0):
                data.append([tweet['retweet_count'], 'Retweet', 'Pro-ED'])
                data.append([tweet['favorite_count'], 'Favorite', 'Pro-ED'])
            if prec_sub and (len(pred_sub) == 0):
                data.append([tweet['retweet_count'], 'Retweet', 'Pro-Rec.'])
                data.append([tweet['favorite_count'], 'Favorite', 'Pro-Rec.'])
            if prec_sub and pred_sub:
                data.append([tweet['retweet_count'], 'Retweet', 'Mixed.'])
                data.append([tweet['favorite_count'], 'Favorite', 'Mixed.'])
    df = pd.DataFrame(data, columns=['Count', 'Action', 'Cluster'])
    pickle.dump(df, open('data/tweet-prelence.pick', 'w'))

    df = pickle.load(open('data/tweet-prelence.pick', 'r'))
    df['Cluster'] = df['Cluster'].map({'Pro-ED': 'Pro-ED Topic',
                                       'Pro-Rec.': 'Pro-Rec. Topic',
                                       'Mixed.': 'Mixed Topic'})

    df.rename(columns={'Cluster': 'Topic'
                       },
              inplace=True)
    plu.plot_config()
    g = sns.factorplot(x="Action", y="Count", hue="Topic", data=df, kind="bar", legend=False, palette={"Pro-ED Topic": "r",
                                                                                                       "Pro-Rec. Topic": "g",
                                                                                                       'Mixed Topic': 'black'})
    plt.legend(loc='best')
    plt.show()


def sentiment_quanti(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    # tweet.txt: only contain tweets that have proed or pro-recovery hashtags, not retweets
    # retweet.txt: contain tweets and retweets that have proed or pro-recovery hashtags
    # all-tweet.txt: contain all tweets and retweets that have proed or pro-recovery and other hashtags
    # only-tweet.txt: contain only tweets that have pro-ed, pro-rec or other tags
    # this analysis should use all-tweet.txt, retweets also indicate agree

    user_net = gt.Graph.Read_GraphML(filename)
    cluster1 = user_net.subgraph(user_net.vs(cluster=0))
    cluster2 = user_net.subgraph(user_net.vs(cluster=1))
    cluster1_uid = cluster1.vs['name']
    cluster2_uid = cluster2.vs['name']
    ped = set(iot.read_ed_pro_hashtags())
    pre = set(iot.read_ed_recovery_hashtags())

    times = dbt.db_connect_col('fed', 'ed_tag')
    for i, ulist in enumerate([cluster1_uid, cluster2_uid]):
        for uid in ulist:
            for tweet in times.find({'user.id': int(uid)}):
                # if 'retweeted_status' in tweet:
                #     continue
                # elif 'quoted_status' in tweet:
                #     continue
                # else:
                hashtags = tweet['entities']['hashtags']
                hash_set = set()
                for hash in hashtags:
                    hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
                pred_sub = hash_set.intersection(ped)
                prec_sub = hash_set.intersection(pre)
                remain = hash_set - pred_sub - prec_sub
                pred_sub_size = len(pred_sub)
                prec_sub_size = len(prec_sub)
                # if pred_sub_size > 0 or prec_sub_size > 0: # only consider pro-ed or pro-rec. content

                text = tweet['text'].encode('utf8')
                text = rtgrex.sub('', text)
                text = mgrex.sub('', text)
                text = hgrex.sub('', text)
                text = ugrex.sub('', text)
                words = text.split()
                if len(words) > 0:
                    print str(i)+'\t'+ str(uid)+'\t' + str(tweet['id'])+'\t' + ' '.join(words) + \
                          '\t'+ '-1:'+' '.join(list(pred_sub)) + \
                          '\t'+ '1:'+' '.join(list(prec_sub)) + \
                          '\t' + '0:'+' '.join(list(remain))
                # cluster, uid, tid, text, -1:pro-ED tags 1:pro-rec. tags 0:ED tags sentiment


def analysis_sentiments(file='tweets.txt'):
    '''Plot sentiment distribution'''
    data = []
    users_topics = {('A', 0): [],
                    ('A', 1): [],
                    ('A', 2): [],
                    ('A', 3): [],
                    ('B', 0): [],
                    ('B', 1): [],
                    ('B', 2): [],
                    ('B', 3): [],
                    }

    all_tweets, both_tweets = 0, 0
    with open(file, 'r') as fo:
        for line in fo.readlines():
            all_tweets += 1
            tokens = line.strip().split('\t')
            label = int(tokens[0])
            uid = tokens[1]
            sentiment = int(tokens[-1])
            ped = tokens[4]
            prec = tokens[5]
            c = 0
            if len(ped)>3:
                c += 1
            if len(prec)>2:
                c += 1

            if c==1:
                if label==0 and len(ped)>3:
                    # AA.append(float(sentiment)/c)
                    data.append(['A', 0, float(sentiment)])
                    users_topics[('A', 0)].append(uid)
                if label==0 and len(prec)>2:
                    # AB.append(float(sentiment)/c)
                    data.append(['A', 1, float(sentiment)])
                    users_topics[('A', 1)].append(uid)
                if label==1 and len(ped)>3:
                    # BA.append(float(sentiment)/c)
                    data.append(['B', 0, float(sentiment)])
                    users_topics[('B', 0)].append(uid)
                if label == 1 and len(prec)>2:
                    # BB.append(float(sentiment)/c)
                    data.append(['B', 1, float(sentiment)])
                    users_topics[('B', 1)].append(uid)
            elif c == 2:
                both_tweets += 1
                if label == 0:
                    data.append(['A', 2, float(sentiment)])
                    users_topics[('A', 2)].append(uid)
                if label == 1:
                    data.append(['B', 2, float(sentiment)])
                    users_topics[('B', 2)].append(uid)
            else:
                if label == 0:
                    data.append(['A', 3, float(sentiment)])
                    users_topics[('A', 3)].append(uid)
                if label == 1:
                    data.append(['B', 3, float(sentiment)])
                    users_topics[('B', 3)].append(uid)
            # add average for all
            if label == 0:
                data.append(['A', 4, float(sentiment)])
            if label == 1:
                data.append(['B', 4, float(sentiment)])

    print both_tweets, all_tweets, float(both_tweets/all_tweets)
    df = pd.DataFrame(data, columns=['Strata', 'Topic', 'Sentiment'])
    # print np.mean(df[(df['Strata']=='A')&(df['Topic']==1)]['Sentiment'])

    #change values in colcumn
    print statu.utest(df[(df.Strata=='A') & (df.Topic==0)]['Sentiment'], df[(df.Strata=='B') & (df.Topic==0)]['Sentiment'])
    print statu.utest(df[(df.Strata=='A') & (df.Topic==1)]['Sentiment'], df[(df.Strata=='B') & (df.Topic==1)]['Sentiment'])
    print statu.utest(df[(df.Strata=='A') & (df.Topic==2)]['Sentiment'], df[(df.Strata=='B') & (df.Topic==2)]['Sentiment'])
    print statu.utest(df[(df.Strata=='A') & (df.Topic==3)]['Sentiment'], df[(df.Strata=='B') & (df.Topic==3)]['Sentiment'])
    print statu.utest(df[(df.Strata=='A') & (df.Topic==4)]['Sentiment'], df[(df.Strata=='B') & (df.Topic==4)]['Sentiment'])


    def mean_std(list):
        return [np.mean(list), np.std(list)]

    amean, astd = mean_std(df[(df.Strata=='A') & (df.Topic==4)]['Sentiment'])
    bmean, bstd = mean_std(df[(df.Strata=='B') & (df.Topic==4)]['Sentiment'])

    # Change abosulate value to z-sore.
    data2 = []
    for index, row in df.iterrows():
        if row['Strata'] == 'A':
            m, st = amean, astd
        else:
            m, st = bmean, bstd
        if row.Topic!=4:
            data2.append([row['Strata'], row['Topic'], (row['Sentiment']-m)/st])
        # data2.append([row['Strata'], row['Topic'], row['Sentiment']])
    df = pd.DataFrame(data2, columns=['Strata', 'Topic', 'Sentiment'])
    #---------------------------------

    annots = [mean_std(df[(df.Strata=='A') & (df.Topic==0)]['Sentiment']),
              mean_std(df[(df.Strata=='A') & (df.Topic==1)]['Sentiment']),
              mean_std(df[(df.Strata=='A') & (df.Topic==2)]['Sentiment']),
              mean_std(df[(df.Strata=='A') & (df.Topic==3)]['Sentiment']),
              mean_std(df[(df.Strata=='A') & (df.Topic==4)]['Sentiment']),
          mean_std(df[(df.Strata=='B') & (df.Topic==0)]['Sentiment']),
          mean_std(df[(df.Strata=='B') & (df.Topic==1)]['Sentiment']),
          mean_std(df[(df.Strata=='B') & (df.Topic==2)]['Sentiment']),
          mean_std(df[(df.Strata=='B') & (df.Topic==3)]['Sentiment']),
          mean_std(df[(df.Strata=='B') & (df.Topic==4)]['Sentiment'])
          ]

    df['Strata'] = df['Strata'].map({'A': 'Group A', 'B': 'Group B'})

    plu.plot_config()
    hatches = ['/', '/','/','/','\\','\\','\\','\\','\\','\\']
    g = sns.factorplot(x="Topic", y="Sentiment", hue="Strata", data=df,
                       kind="bar", legend=False, palette={"Group A": "#e9a3c9", "Group B": "#a1d76a"})
    ax=g.ax #annotate axis = seaborn axis
    for i, p in enumerate(ax.patches):
        p.set_hatch(hatches[i])
        # ax.annotate("%.2f" %(annots[i][0]), (p.get_x() + p.get_width() / 2., p.get_height() if p.get_y()>=0 else -0.2-p.get_height()),
        #      ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
        #      textcoords='offset points')
    g.set_xticklabels(["Pro-ED", "Pro-Rec.", "Mixed", "Unspecified"])
    g.set_ylabels('Relative Sentiment')
    g.set_xlabels('Theme')
    plt.legend(loc='upper center')
    # plt.legend(bbox_to_anchor=(1, 1.2))
    plt.show()


    '''Proportion of tweets in each type of topic'''

    df['Strata'] = df['Strata'].map({'Group A': 'A', 'Group B': 'B'})
    dat = []
    A = len(df[(df.Strata=='A') & (df.Topic!=4)])
    B = len(df[(df.Strata=='B') & (df.Topic!=4)])
    print A, B
    print float(A)/(A+B), float(B)/(A+B)
    AAc = len(df[(df.Strata=='A') & (df.Topic==0)])
    dat.append(['A', 0, float(AAc)/A])
    ABc = len(df[(df.Strata=='A') & (df.Topic==1)])
    dat.append(['A', 1, float(ABc)/A])
    ACc = len(df[(df.Strata=='A') & (df.Topic==2)])
    dat.append(['A', 2, float(ACc)/A])
    ADc = len(df[(df.Strata=='A') & (df.Topic==3)])
    dat.append(['A', 3, float(ADc)/A])
    print AAc,ABc,ACc,ADc

    BAc = len(df[(df.Strata=='B') & (df.Topic==0)])
    dat.append(['B', 0, float(BAc)/B])
    BBc = len(df[(df.Strata=='B') & (df.Topic==1)])
    dat.append(['B', 1, float(BBc)/B])
    BCc = len(df[(df.Strata=='B') & (df.Topic==2)])
    dat.append(['B', 2, float(BCc)/B])
    BDc = len(df[(df.Strata=='B') & (df.Topic==3)])
    dat.append(['B', 3, float(BDc)/B])
    print BAc, BBc, BCc, BDc


    pro = pd.DataFrame(dat, columns=['Strata', 'Topic', 'Proportion'])
    pro['Strata'] = pro['Strata'].map({'A': 'Group A', 'B': 'Group B'})
    plu.plot_config()
    g = sns.factorplot(x="Topic", y="Proportion", hue="Strata", legend=False, kind="bar", data=pro,
                       palette={"Group A": "#e9a3c9", "Group B": "#a1d76a"})
    g.set_xticklabels(["Pro-ED", "Pro-Rec.", "Mixed", "Unspecified"])
    g.set_ylabels('Tweet Proportion')
    g.set_xlabels('Theme')
    annots = [AAc,ABc,ACc,ADc, BAc, BBc, BCc, BDc]
    ax=g.ax #annotate axis = seaborn axis
    for i, p in enumerate(ax.patches):
         # ax.annotate("{:,}".format(annots[i]), (p.get_x() + p.get_width() / 2., p.get_height()),
         #     ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
         #     textcoords='offset points')
         p.set_hatch(hatches[i])
    plt.legend(loc='upper right')
    # plt.legend(bbox_to_anchor=(1, 1.2))
    plt.show()


    '''User proportion'''
    user_net = gt.Graph.Read_GraphML('data/communication-only-fed-filter-hashtag-cluster.graphml')
    gt.summary(user_net)
    cluster1 = user_net.subgraph(user_net.vs(cluster=0))
    cluster2 = user_net.subgraph(user_net.vs(cluster=1))
    cluster1_usize = len(cluster1.vs)
    cluster2_usize = len(cluster2.vs)
    print cluster1_usize, cluster2_usize
    user_net.vs.select(name_in=users_topics[('A',1)])['cluster'] = 2
    user_net.vs.select(name_in=users_topics[('B',0)])['cluster'] = 3
    # user_net.write_graphml('interpost-test'+'.graphml')
    dat = []
    clist = [len(set(users_topics[('A',0)])),
             len(set(users_topics[('A',1)])),
             len(set(users_topics[('A',2)])),
             len(set(users_topics[('A',3)])),
             len(set(users_topics[('B',0)])),
             len(set(users_topics[('B',1)])),
             len(set(users_topics[('B',2)])),
             len(set(users_topics[('B',3)]))
             ]
    for c, t in users_topics.keys():
        ulen = len(set(users_topics[(c,t)]))
        print c, t, ulen
        if c == 'A':
            dat.append([c, t, float(ulen)/cluster1_usize])
        else:
            dat.append([c, t, float(ulen)/cluster2_usize])
    pro = pd.DataFrame(dat, columns=['Strata', 'Topic', 'Proportion'])
    pro['Strata'] = pro['Strata'].map({'A': 'Group A', 'B': 'Group B'})

    plu.plot_config()
    g = sns.factorplot(x="Topic", y="Proportion", hue="Strata", legend=False, kind="bar", data=pro,
                       palette={"Group A": "#e9a3c9", "Group B": "#a1d76a"})
    g.set_xticklabels(["Pro-ED", "Pro-Rec.", "Mixed", "Unspecified"])
    g.set_ylabels('User Proportion')
    g.set_xlabels('Theme')
    annots = clist
    ax=g.ax #annotate axis = seaborn axis
    for i, p in enumerate(ax.patches):
         # ax.annotate("{:,}".format(annots[i]), (p.get_x() + p.get_width() / 2., p.get_height()),
         #     ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
         #     textcoords='offset points')
         p.set_hatch(hatches[i])

    plt.legend(loc='upper right')
    # plt.legend(bbox_to_anchor=(1, 1.2))
    plt.show()





def liwc_sim(filename='data/cluster-feature.data'):
    '''Calculate the similarity of two clusters of users, in terms of LIWC'''
    X, y = load_svmlight_file(filename)
    X = X.toarray()
    print X.shape
    fields = iot.read_fields()
    trim_files = [f.split('.')[-1] for f in fields]
    print len(trim_files)
    select_f = [
        'friend_count', 'status_count', 'follower_count',
        'friends_day', 'statuses_day', 'followers_day',
        'retweet_pro',
        'dmention_pro', 'reply_pro',
        # 'hashtag_pro',
        # 'url_pro',
        'retweet_div',
        'mention_div',
        'reply_div',
        'i', 'we', 'swear', 'negate', 'body', 'health',
        'ingest', 'social', 'posemo', 'negemo']
    indecs = [trim_files.index(f) for f in select_f]
    X = X[:, indecs]
    print X.shape

    # '''Calculate positive emotion ratio'''
    # X[:, -2] /= (X[:, -2] + X[:, -1])
    # X = X[:, :-1]
    # X[:, -1][~np.isfinite(X[:, -1])] = 0
    # print X.shape

    #scaling
    min_max_scaler = preprocessing.MinMaxScaler()
    X = min_max_scaler.fit_transform(X)

    # X = preprocessing.scale(X)

    sims = cosine_similarity(X)
    length = len(X)
    AA, BB, AB = [], [], []
    # data = []
    for i in xrange(length):
        for j in xrange(i+1, length):
            if y[i] == y[j]:
                if y[i] == 0:
                    # data.append([sims[i][j], 'A-A'])
                    AA.append(sims[i][j])
                elif y[i] == 1:
                    # data.append([sims[i][j], 'B-B'])
                    BB.append(sims[i][j])
            else:
                # data.append([sims[i][j], 'A-B'])
                AB.append(sims[i][j])
    # df = pd.DataFrame(data, columns=['cos', 'pair'])

    print statu.utest(AA, BB)
    print statu.utest(AA, AB)
    print statu.utest(AB, BB)

    plu.plot_config()
    sns.distplot(AA, hist=False, kde_kws={"color": "r", "lw": 2, "marker": 'o'}, label='Pro-ED ($\mu=%0.2f \pm %0.2f$)' % (np.mean(AA), np.std(AA)))
    sns.distplot(BB, hist=False, kde_kws={"color": "g", "lw": 2, "marker": 's'}, label='Pro-Rec. ($\mu=%0.2f \pm %0.2f$)' % (np.mean(BB), np.std(BB)))
    sns.distplot(AB, hist=False, kde_kws={"color": "k", "lw": 2, "marker": '^'}, label='Cross-Clust. ($\mu=%0.2f \pm %0.2f$)' % (np.mean(AB), np.std(AB)))
    # sns.distplot(AA+BB+AB, hist=False)
    plt.axvline(np.mean(AA), linestyle='dashdot',
                    c='r', lw=4)
    plt.axvline(np.mean(BB), linestyle='dashdot',
                    c='g', lw=4)
    plt.axvline(np.mean(AB), linestyle='dashdot',
                    c='k', lw=4)

    # plt.xlim(0, 1)
    plt.legend(loc="best")
    plt.xlabel('cos(a,b)')
    plt.ylabel('P(cos(a,b))')
    plt.show()



    # df.to_csv('cos.csv', index=False)



def regression(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''Regression for pro-ed and pro-recovery users'''
    user_net = gt.Graph.Read_GraphML(filename)
    cluster1 = user_net.subgraph(user_net.vs(cluster=0))
    cluster2 = user_net.subgraph(user_net.vs(cluster=1))
    cluster1_uid = cluster1.vs['name']
    cluster2_uid = cluster2.vs['name']
    fw = open('data/cluster-feature.data', 'w')
    # print cluster1_uid
    # print cluster2_uid

    com = dbt.db_connect_col('fed', 'com')
    fields = iot.read_fields()
    trimed_fields = [field.split('.')[-1] for field in fields]
    data = []
    for i, ulist in enumerate([cluster1_uid, cluster2_uid]):
        for uid in ulist:
            user = com.find_one({'id': int(uid), 'liwc_anal.result.WC': {'$exists': True}})
            if user:
                values = iot.get_fields_one_doc(user, fields)
                data.append([uid, i] + values)
                outstr = str(i) + ' '
                for j in xrange(len(values)):
                    outstr += str(j+1)+':'+str(values[j])+' '
                fw.write(outstr+'\n')
    df = pd.DataFrame(data, columns=['uid', 'label']+trimed_fields)
    df.to_csv('data/cluster-feature.csv')
    fw.close()


def assortative_test(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''Test assortative of network in terms of cluster assignments'''
    g = gt.Graph.Read_GraphML(filename)
    raw_values = np.array(g.vs['cluster'])
    raw_assort = g.assortativity('cluster', 'cluster', directed=True)
    modu = g.modularity(g.vs['cluster'], weights='weight')
    print raw_assort, modu
    ass_list = list()
    for i in xrange(3000):
        np.random.shuffle(raw_values)
        g.vs["cluster"] = raw_values
        ass_list.append(g.assortativity('cluster', 'cluster', directed=True))
    ass_list = np.array(ass_list)
    amean, astd = np.mean(ass_list), np.std(ass_list)

    absobserved = abs(raw_assort)
    pval = (np.sum(ass_list >= absobserved) +
            np.sum(ass_list <= -absobserved))/float(len(ass_list))
    zscore = (raw_assort-amean)/astd
    if pval < 0.05:
        mark = '*'
    if pval < 0.01:
        mark = '**'
    if pval < 0.001:
        mark = '***'
    print ('Raw assort: %.3f, mean: %.3f std: %.3f z: %.3f, p: %.100f %s' %(raw_assort, amean, astd, zscore, pval, mark))

def binArray(data, binsize, func=np.nanmean, axis=0):
    # Bin data and return means
    data = np.array(data)
    dims = np.array(data.shape)
    argdims = np.arange(data.ndim)
    argdims[0], argdims[axis]= argdims[axis], argdims[0]
    data = data.transpose(argdims)
    data = [func(np.take(data,np.arange(int(i*binsize),int(i*binsize+binsize)),0),0) for i in np.arange(dims[axis]//binsize)]
    data = np.array(data).transpose(argdims)
    return data

def compare_in_out_degree(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    # # Compare the relation between in and out degree in two clustsers of users, degrees are from two sub-networks
    # g = gt.Graph.Read_GraphML(filename)
    # gt.summary(g)
    #
    # cl1 = g.vs.select(cluster=0)
    # cl2 = g.vs.select(cluster=1)
    # g1 = g.subgraph(cl1)
    # g2 = g.subgraph(cl2)
    # gt.net_stat(g1)
    # gt.net_stat(g2)
    # g1 = gt.giant_component(g1)
    # g2 = gt.giant_component(g2)
    # gt.net_stat(g1)
    # gt.net_stat(g2)
    #
    # # BUG of igraph https://github.com/igraph/python-igraph/issues/64
    # data = []
    # for i, net in enumerate([g1, g2]):
    #     label = ['Pro-ED', 'Pro-Rec.'][i]
    #     for v in net.vs:
    #         sout = sum(net.es.select(_source=v.index)['weight'])
    #         sin = sum(net.es.select(_target=v.index)['weight'])
    #         dout = len(net.es.select(_source=v.index))
    #         din = len(net.es.select(_target=v.index))
    #         data.append([dout, din, sout, sin, label])
    # df = pd.DataFrame(data, columns=['d_out', 'd_in', 's_out', 's_in', 'Cluster'])
    # pickle.dump(df, open('dfed.pick', 'w'))

    df = pickle.load(open('dfed.pick', 'r'))
    plu.plot_config()
    xa, ya = df[df['Cluster']=='Pro-ED']['s_out'], df[df['Cluster']=='Pro-ED']['s_in']
    xb, yb = df[df['Cluster']=='Pro-Rec.']['s_out'], df[df['Cluster']=='Pro-Rec.']['s_in']

    xas = xa[(xa>0)&(ya>0)]
    yas = ya[(xa>0)&(ya>0)]
    xbs = xb[(xb>0)&(yb>0)]
    ybs = yb[(xb>0)&(yb>0)]
    # xas = xa
    # yas = ya
    # xbs = xb
    # ybs = yb
    xass, yass = (list(t) for t in zip(*sorted(zip(xas, yas))))
    xbss, ybss = (list(t) for t in zip(*sorted(zip(xbs, ybs))))

    xameans = binArray(xass, len(xas)/15)
    yameans = binArray(yass, len(yas)/15)
    print xameans, yameans
    xbmeans = binArray(xbss, len(xbs)/15)
    ybmeans = binArray(ybss, len(ybs)/15)
    print xbmeans, ybmeans

    ax = sns.regplot(x=xameans, y=yameans, color="r",scatter_kws={"s": 100}, lowess=True,
                     label='Pro-ED: '+r'$\tau(s_{out}, s_{in})$'+' = %.2f' %(statu.stats.kendalltau(xas, yas))[0])
    print statu.stats.kendalltau(xas, yas)
    sns.regplot(ax=ax, x=xbmeans, y=ybmeans, color="g", marker='^', scatter_kws={"s": 100},lowess=True,
                 label=r'Pro-Rec.: '+r'$\tau(s_{out}, s_{in})$'+' = %.2f' %(statu.stats.kendalltau(xbs, ybs))[0])
    print statu.stats.kendalltau(xbs, ybs)

    plt.legend(loc="best", frameon=True)
    plt.xlabel(r'$s_{out}$')
    plt.ylabel(r'$s_{in}$')
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.show()




    # xa = np.log(1+xa)
    # ya = np.log(1+ya)
    # xb = np.log(1+xb)
    # yb = np.log(1+yb)
    # g = sns.JointGrid(xa, ya)
    # g.plot_joint(sns.regplot, color="r", label='Pro-ED: '+r'$\tau$'+' = %.2f' %(statu.stats.kendalltau(xa, ya))[0])
    # g.annotate(statu.stats.kendalltau)
    # g.x = xb
    # g.y = yb
    # g.plot_joint(plt.scatter, marker='^', s=50, color="g", label=r'Pro-Rec.: '+r'$\tau$'+' = %.2f' %(statu.stats.kendalltau(xb, yb))[0])
    # g.plot_joint(sns.regplot, color="g")
    # g.annotate(statu.stats.kendalltau)
    # g.ax_marg_x.set_axis_off()
    # g.ax_marg_y.set_axis_off()
    # plt.legend(loc="best", frameon=True)
    # plt.xlabel(r'$\log(1+d_{in})$')
    # plt.ylabel(r'$\log(1+d_{out})$')
    # # sns.pairplot(df, kind="reg", hue="Cluster", palette={"Pro-ED": "r", "Pro-Rec.": "g"})
    # # plt.legend(loc="best", frameon=True)
    # plt.show()


def compare_in_out_degree_allconnection(allnet='data/fed-communication.graphml', filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''Network built by all tweets, not just for ED-related tweets'''
    # # Compare the relation between in and out degree in two clustsers of users.
    # g = gt.Graph.Read_GraphML(allnet)
    # gt.summary(g)
    #
    # ged = gt.Graph.Read_GraphML(filename)
    # gt.summary(ged)
    #
    # vs = g.vs.select(name_in=ged.vs['name'])
    # g = g.subgraph(vs)
    # gt.summary(g)
    # g.write_graphml('data/communication-all'+'.graphml')
    #
    # cl1 = ged.vs.select(cluster=0)['name']
    # cl2 = ged.vs.select(cluster=1)['name']
    #
    # gcl1 = g.vs.select(name_in=cl1)
    # gcl2 = g.vs.select(name_in=cl2)
    # # g1 = g.subgraph(g.vs(name_in=cl1))
    # # g2 = g.subgraph(g.vs(name_in=cl2))
    # # gt.net_stat(g1)
    # # gt.net_stat(g2)
    # # g1 = gt.giant_component(g1)
    # # g2 = gt.giant_component(g2)
    # # gt.net_stat(g1)
    # # gt.net_stat(g2)
    #
    # # inds1 = g1.indegree()
    # # outds1 = g1.outdegree()
    # # inds2 = g2.indegree()
    # # outds2 = g2.outdegree()
    #
    # # plu.plot_config()
    # # figPDF = powerlaw.plot_pdf(np.array(inds1)+1, color='r')
    # # powerlaw.plot_pdf(np.array(inds1)+1, linear_bins=True, color='r', ax=figPDF)
    # # powerlaw.plot_pdf(np.array(inds2)+1, color='g', ax=figPDF)
    # # powerlaw.plot_pdf(np.array(inds2)+1, linear_bins=True, color='g', ax=figPDF)
    # # figPDF.set_ylabel("p(X)")
    # # figPDF.set_xlabel(r"Indegree")
    # # plt.show()
    #
    # # BUG of igraph https://github.com/igraph/python-igraph/issues/64
    # data = []
    # for i, net in enumerate([gcl1, gcl2]):
    #     label = ['Pro-ED', 'Pro-Rec.'][i]
    #     for v in net:
    #         sout = sum(g.es.select(_source=v.index)['weight'])
    #         sin = sum(g.es.select(_target=v.index)['weight'])
    #         dout = len(g.es.select(_source=v.index))
    #         din = len(g.es.select(_target=v.index))
    #         data.append([dout, din, sout, sin, label])
    # df = pd.DataFrame(data, columns=['d_out', 'd_in', 's_out', 's_in', 'Cluster'])
    # pickle.dump(df, open('dfall.pick', 'w'))

    df = pickle.load(open('dfall.pick', 'r'))
    plu.plot_config()
    xa, ya = df[df['Cluster']=='Pro-ED']['s_in'], df[df['Cluster']=='Pro-ED']['s_out']
    xb, yb = df[df['Cluster']=='Pro-Rec.']['s_in'], df[df['Cluster']=='Pro-Rec.']['s_out']
    print len(xa), len(ya)
    print len(xa[xa>0]) , len(ya[ya>0]), float(len(xa[xa>0]))/len(xa), float(len(ya[ya>0]))/len(ya)
    print len(xb), len(yb)
    print len(xb[xb>0]) , len(yb[yb>0]), float(len(xb[xb>0]))/len(xb), float(len(yb[yb>0]))/len(yb)


    xa = np.log(1+xa)
    ya = np.log(1+ya)
    xb = np.log(1+xb)
    yb = np.log(1+yb)
    g = sns.JointGrid(xa, ya)
    g.plot_joint(sns.regplot, color="r", label='Pro-ED: '+r'$\tau$'+' = %.2f' %(statu.stats.kendalltau(xa, ya))[0])
    g.annotate(statu.stats.kendalltau)
    g.x = xb
    g.y = yb
    g.plot_joint(plt.scatter, marker='^', s=50, color="g", label=r'Pro-Rec.: '+r'$\tau$'+' = %.2f' %(statu.stats.kendalltau(xb, yb))[0])
    g.plot_joint(sns.regplot, color="g")
    g.annotate(statu.stats.kendalltau)
    g.ax_marg_x.set_axis_off()
    g.ax_marg_y.set_axis_off()
    plt.legend(loc="best", frameon=True)
    plt.xlabel(r'$\log(1+s_{in})$')
    plt.ylabel(r'$\log(1+s_{out})$')


    # sns.pairplot(df, kind="reg", hue="Cluster", palette={"Pro-ED": "r", "Pro-Rec.": "g"})
    # plt.legend(loc="best", frameon=True)
    plt.show()


def split_in_out_degree(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    # Compare the relation between in and out degree in two clustsers of users, degrees are measured from whole network
    g = gt.Graph.Read_GraphML(filename)
    gt.summary(g)

    cl1 = g.vs.select(cluster=0)
    cl2 = g.vs.select(cluster=1)
    inds1 = np.array(g.indegree(cl1))
    outds1 = np.array(g.outdegree(cl1))
    inds2 = np.array(g.indegree(cl2))
    outds2 = np.array(g.outdegree(cl2))

    print len(inds1), len(outds1)
    print statu.stats.kendalltau(inds1, outds1)

    print len(inds1[inds1>0]), len(outds1[outds1>0])
    xa = inds1[(inds1>0)&(outds1>0)]
    ya = outds1[(inds1>0)&(outds1>0)]

    print len(xa), len(ya)
    print statu.stats.kendalltau(xa, ya)

    print len(inds2), len(outds2)
    print statu.stats.kendalltau(inds2, outds2)
    print len(inds2[inds2>0]), len(outds2[outds2>0])
    xa = inds2[(inds2>0)&(outds2>0)]
    ya = outds2[(inds2>0)&(outds2>0)]
    print len(xa), len(ya)
    print statu.stats.kendalltau(xa, ya)

    # sns.distplot(np.array(inds2), kde=True)
    # sns.distplot(np.array(inds1))

    # plt.show()


def interaction_ratio(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''Test interaction of different clusters of users, see political polariztion on twitter'''
    g = gt.Graph.Read_GraphML(filename)
    a = g.vs(cluster=0)
    b = g.vs(cluster=1)

    la = len(a)
    lb = len(b)


    sa = sum(g.es.select(_source_in = a)['weight'])
    sb = sum(g.es.select(_source_in = b)['weight'])

    aa = sum(g.es.select(_source_in = a, _target_in = a)['weight'])
    ab = sum(g.es.select(_source_in = a, _target_in = b)['weight'])
    ba = sum(g.es.select(_source_in = b, _target_in = a)['weight'])
    bb = sum(g.es.select(_source_in = b, _target_in = b)['weight'])

    eaa = float(sa)*(la)/(la+lb)
    eab = float(sa)*(lb)/(la+lb)
    eba = float(sb)*(la)/(la+lb)
    ebb = float(sb)*(lb)/(la+lb)

    print ('A: %d B: %d ' %(len(a), len(b)))
    print ('%d %d %d %d ' %(aa, ab, ba, bb))
    print ('%.2f %.2f %.2f %.2f ' %(eaa, eab, eba, ebb))
    print ('%.3f %.3f %.3f %.3f ' %(float(aa-eaa)/eaa, float(ab-eab)/eab, float(ba-eba)/eba, float(bb-ebb)/ebb))
    # print ('%.3f %.3f %.3f %.3f ' %(float(aa)/eaa, float(ab)/eab, float(ba)/eba, float(bb)/ebb))


def prominence(filename='data/communication-only-fed-filter-hashtag-cluster.graphml',
               tagfile='data/user-hash-vector.pick'
                ):
    # TODO calculate the prominence of hashtag
    g = gt.Graph.Read_GraphML(filename)
    user_tag = pickle.load(open(tagfile, 'r')) # {'uid': 'tag1 tag2 tag3'}

    uid_lable = dict(zip(g.vs['name'], g.vs['cluster']))
    clusterA, clusterB = [], []
    clusterA_user_no, clusterB_user_no = [], [] #count how many users have used a tag
    for uid in user_tag.keys():
        tag_list = user_tag[uid].split()
        if uid_lable[str(uid)] == 0:
            clusterA += tag_list
            clusterA_user_no += list(set(tag_list))
        elif uid_lable[str(uid)] == 1:
            clusterB += tag_list
            clusterB_user_no += list(set(tag_list))
        else:
            print 'not existing cluster'
    NA = len(clusterA)
    NB = len(clusterB)
    NALL = NA + NB

    Acounter = Counter(clusterA)
    Bcounter = Counter(clusterB)
    Allcounter = Counter(clusterA + clusterB) # counting how many times of a tag being used
    Allcounter_user = Counter(clusterA_user_no + clusterB_user_no) # counting how many users using a tag

    tags = set(Acounter.keys() + Bcounter.keys())
    valance = {}
    for tag in tags:
        '''Self defined values'''
        if Allcounter.get(tag, 0) > 3 and Allcounter_user.get(tag, 0) > 3:
            fa = Acounter.get(tag, 0)
            fb = Bcounter.get(tag, 0)
            pa = float(fa)/NA
            pb = float(fb)/NB
            pall = pa + pb
            if pall > 0:
                v = ((pb - pa)/(pa + pb))
                if pb >= pa:
                    v *= np.log(fb)
                else:
                    v *= np.log(fa)
                valance[tag] = v
                print tag, fa, fb, v
            else:
                print tag, '-------------------------------------'
        '''PMI'''
        # TALL = Allcounter.get(tag, 0)
        # if TALL > 3 and Allcounter_user.get(tag, 0) > 3:
        #     fa = Acounter.get(tag, 0)
        #     fb = Bcounter.get(tag, 0)
        #     if fa>0:
        #         pmiA = np.log(float(fa*NALL)/(TALL*NA))/(-np.log(float(fa)/NALL))
        #         # pmiA = np.log(float(fa*NALL)/(TALL*NA))
        #     else:
        #         pmiA = 0
        #     if fb > 0:
        #         pmiB = np.log(float(fb*NALL)/(TALL*NB))/(-np.log(float(fb)/NALL))
        #         # pmiB = np.log(float(fb*NALL)/(TALL*NB))
        #     else:
        #         pmiB = 0
        #     value = pmiB - pmiA
        #     valance[tag] = value
        #     print tag, fa, fb, TALL, pmiA, pmiB, value
        #     # if fa > 0:
        #     #     pmiB = np.log(float(fa*NALL)/(TALL*NA))/(-np.log(float(fa)/NALL))
        #     # else:
        #     #     pmiB = 0
        #     # valance[tag] = pmiB

    # pickle.dump(valance, open('data/hashtag-valance.pick', 'w'))
    # valance = pickle.load(open('data/hashtag-valance.pick', 'r'))
    plu.plot_config()
    x = valance.values()
    print np.min(x), np.percentile(x, 25), np.percentile(x, 50), np.percentile(x, 75), np.max(x)

    # bin = np.linspace(min(x), max(x), 100)
    sns.distplot(x)
    plt.xlabel(r'PI(h)')
    plt.ylabel('PDF')
    plt.show()

def compare_liwc(filepath='data/cluster-feature.data'):
    '''Compare difference between two clusters of users
    The input file is from classifier/cross_val.py'''
    X, y = load_svmlight_file(filepath)
    X = X.toarray()
    fields = iot.read_fields()
    trim_files = [f.split('.')[-1] for f in fields]
    print len(trim_files)
    select_f = [
        'friend_count', 'status_count', 'follower_count',
        'friends_day', 'statuses_day', 'followers_day',
        'retweet_pro',
        'dmention_pro', 'reply_pro',
        # 'hashtag_pro',
        # 'url_pro',
        'retweet_div',
        'mention_div',
        'reply_div',
        'i', 'we', 'swear', 'negate', 'body', 'health',
        'ingest', 'social', 'posemo', 'negemo']

    indecs = [trim_files.index(f) for f in select_f]
    print indecs
    X = X[:, indecs]

    '''Calculate positive emotion ratio'''
    # print X.shape
    # X[:,-2] /= (X[:,-2] + X[:, -1])
    # X = X[:, :-1]
    # X[:, -1][~np.isfinite(X[:, -1])] = 0

    # min_max_scaler = preprocessing.MinMaxScaler()
    # X = min_max_scaler.fit_transform(X)

    # X = preprocessing.scale(X)

    print X.shape, y.shape
    Z = np.append(X, y.reshape((len(y), 1)), axis=1)
    df = pd.DataFrame(Z, columns=select_f + ['label'])
    # affair_mod = logit("label ~ " + '+'.join(select_f[:-1]), df).fit()
    # print(affair_mod.summary())

    df.rename(columns={'friend_count': '#Fr',
                       'status_count': '#T',
                       'follower_count': '#Fo',
                       'friends_day': '#Fr/D',
                       'statuses_day': '#T/D',
                       'followers_day': '#Fo/D',
                       'retweet_pro': '%RT',
                       'url_pro': '%URL',
                       'dmention_pro': '%@',
                       'reply_pro': '%RP',
                       'retweet_div': '$\Delta$(RT)',
                       'reply_div': '$\Delta$(RP)',
                       'mention_div': '$\Delta$(@)',
                       # 'posemo': 'PER'
                       },
              inplace=True)
    print len(select_f)
    for col in df.columns[:-1]:
        cat1 = df[col][df['label']==0]
        cat2 = df[col][df['label']==1]
        # return mean, std, mean, std, U, P, P-core, Z
        m1, std1, m2, std2, t, p, pm, z = statu.utest(cat1, cat2, len(select_f))
        mark = ''
        if pm < 0.05:
            mark = '*'
        if pm < 0.01:
            mark = '**'
        if pm < 0.001:
            mark = '***'
        print "%s & %.2f $\pm$ %.2f & %.2f $\pm$ %.2f & %.2f & %.3f & %s \\\\" %(col, m1, std1, m2, std2, z, p, mark)


    # data = pd.melt(df, id_vars=['label'])
    # data['label'] = data['label'].map({0.0: 'A', 1.0: 'B'})
    # data.columns = ['Cluster', 'Measure', 'Value']
    # data['Cluster'] = data['Cluster'].map({'A': 'Pro-ED', 'B': 'Pro-Rec.'})
    #
    #
    # plu.plot_config()
    # sns.violinplot(x="Measure", y="Value", hue="Cluster", data=data, split=True,
    #            inner="quart", palette={"Pro-ED": "r", "Pro-Rec.": "g"})
    # # sns.boxplot(x="Measure", y="Value", hue="Cluster", data=data,
    # #             palette={"A": "r", "B": "g"})
    # sns.despine(left=True)
    # plt.legend(loc="best")
    # plt.show()

def mark_pvalue(pval):
    mark = ''
    if pval < 0.05:
        mark = '*'
    if pval < 0.01:
        mark = '**'
    if pval < 0.001:
        mark = '***'
    return mark

def core_analysis(netfilename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    g = gt.Graph.Read_GraphML(netfilename)
    cl1 = g.vs.select(cluster=0)
    cl2 = g.vs.select(cluster=1)
    g1 = g.subgraph(cl1)
    g2 = g.subgraph(cl2)
    gt.net_stat(g1)
    gt.net_stat(g2)
    g1 = gt.giant_component(g1)
    g2 = gt.giant_component(g2)
    gt.net_stat(g1)
    gt.net_stat(g2)

    com = dbt.db_connect_col('fed', 'com')
    timecount = {}
    uids = [int(uid) for uid in g.vs['name']]
    for user in com.find({'id': {'$in': uids}}, ['id', 'timeline_count']):
        timecount[str(user['id'])] = user['timeline_count']

    # g1.write_graphml('ped_net.graphml')
    # g2.write_graphml('prec_net.graphml')

    # g1cen = np.array(g1.strength(mode='ALL',weights='weight'))
    # g2cen = np.array(g2.strength(mode='ALL',weights='weight'))
    g1cen = np.array(g1.pagerank(weights='weight'))
    g2cen = np.array(g2.pagerank(weights='weight'))

    g1.vs['centrality'] = g1cen
    g2.vs['centrality'] = g2cen
    g1.vs['coreness'] = g1.coreness()
    g2.vs['coreness'] = g2.coreness()
    g1_core = dict(zip(g1.vs['name'], g1.vs['centrality']))
    g2_core = dict(zip(g2.vs['name'], g2.vs['centrality']))
    g1_outs = dict(zip(g1.vs['name'], g1.strength(mode='IN', weights='weight')))
    g2_outs = dict(zip(g2.vs['name'], g2.strength(mode='IN', weights='weight')))

    plu.plot_config()
    ###--------------------Plot coreness and ratio of users
    # data = [[val, float(len([cor for cor in g1.vs['coreness'] if cor>= val]))/len(g1.vs['coreness']), 'Pro-ED'] for val, c in Counter(g1.vs['coreness']).items()] \
    #        + [[val, float(len([cor for cor in g2.vs['coreness'] if cor>= val]))/len(g2.vs['coreness']), 'Pro-Rec.'] for val, c in Counter(g2.vs['coreness']).items()]
    # df = pd.DataFrame(data, columns=['Coreness', 'Ratio', 'Group'])
    # sns.factorplot(x="Coreness", y="Ratio", hue="Group", data=df,
    #                size=10, palette={"Pro-ED": "r", "Pro-Rec.": "g"}, legend=False, markers=['o', '^'])
    # # plt.xlim(xmin=0)
    # # plt.ylim(ymin=0)
    # plt.legend(loc='best')
    # plt.xlabel(r'$k$')
    # plt.ylabel(r'Ratio $k$-core Users')
    # plt.show()

    # ------------------------Read sentiments
    user_ped, user_prec, user_tweet, user_sentiment = {}, {}, {}, {}
    with open('all-tweet.txt', 'r') as fo:
        for line in fo.readlines():
            tokens = line.strip().split('\t')
            uid = tokens[1]
            count = user_tweet.get(uid, 0)
            user_tweet[uid] = count + 1
            sentiment = float(tokens[-1])
            sents = user_sentiment.get(uid, [])
            sents.append(sentiment)
            user_sentiment[uid] = sents
            ped = tokens[4]
            prec = tokens[5]
            if len(ped)>3:
                sents = user_ped.get(uid, [])
                sents.append(sentiment)
                user_ped[uid] = sents
            if len(prec)>2:
                sents = user_prec.get(uid, [])
                sents.append(sentiment)
                user_prec[uid] = sents

    # user_ped_zscore, user_prec_zscore = {}, {}
    # for uid in user_ped.keys():
    #     umean, ustd = np.mean(user_sentiment[uid]), np.std(user_sentiment[uid])
    #     if ustd:
    #         user_ped_zscore[uid] = [(v-umean)/ustd for v in user_ped[uid]]
    #     # else:
    #     #     print user_sentiment[uid]
    # for uid in user_prec.keys():
    #     umean, ustd = np.mean(user_sentiment[uid]), np.std(user_sentiment[uid])
    #     if ustd:
    #         user_prec_zscore[uid] = [(v-umean)/ustd for v in user_prec[uid]]
    #     # else:
    #     #     print user_sentiment[uid]


    user_ped_mean = [np.sum(user_ped[uid])/timecount[uid] for uid in user_ped.keys()]
    user_prec_mean = [np.sum(user_prec[uid])/timecount[uid] for uid in user_prec.keys()]

    user_ped_mean_dic = dict(zip(user_ped.keys(), user_ped_mean))
    user_prec_mean_dic = dict(zip(user_prec.keys(), user_prec_mean))



    def kental(d1, d2):
        keys1, keys2 = set(d1.keys()), set(d2.keys())
        val1, val2 = [], []
        for key in keys1.intersection(keys2):
            val1.append(d1[key])
            val2.append(d2[key])
        return statu.stats.kendalltau(val1, val2)
    k1, p1 = kental(user_ped_mean_dic, g1_core)
    k2, p2 = kental(user_prec_mean_dic, g2_core)

    print ', %.2f%s, %.3f, %.2f%s, %.3f' %(k1, mark_pvalue(p1), p1, k2, mark_pvalue(p2), p2)

    k1, p1 = kental(user_ped_mean_dic, g1_outs)
    k2, p2 = kental(user_prec_mean_dic, g2_outs)

    print ', %.2f%s, %.3f, %.2f%s, %.3f' %(k1, mark_pvalue(p1), p1, k2, mark_pvalue(p2), p2)

    #-----plot
    # print max(g1.vs['coreness']), max(g2.vs['coreness'])
    # data = []
    # for i, cendic in enumerate([g1_core, g2_core]):
    #     cenkeys = set(cendic.keys())
    #     for j, sendic in enumerate([user_ped_mean_dic, user_prec_mean_dic]):
    #         senkeys = set(sendic.keys())
    #         if i == j:
    #             for uid in cenkeys.intersection(senkeys):
    #                 # for core in set(cendic.values()):
    #                 #     if cendic[uid] >= core:
    #                 #         data.append([sendic[uid], core, ['Pro-ED', 'Pro-Rec.'][i]])
    #                 for core in range(1, cendic[uid] + 1):
    #                         data.append([sendic[uid], core, ['Pro-ED', 'Pro-Rec.'][i]])
    # df = pd.DataFrame(data, columns=['Sentiment', 'Coreness', 'Group'])
    # sns.factorplot(x='Coreness', y='Sentiment', hue="Group", data=df,
    #                size=10, palette={"Pro-ED": "r",
    #                                  "Pro-Rec.": "g"
    #                                  }, legend=False, markers=['o', '^'])
    # plt.legend(loc='best')
    # plt.xlabel(r'$k$')
    # plt.ylabel(r'Pro-strength of $k$-core Users')
    # plt.show()
    #
    # means = df[df.Group=='Pro-ED'].groupby(['Coreness'])['Sentiment'].mean()
    # print means
    # ks = range(1, max(g1.vs['coreness'])+1)
    # print ks
    # print statu.stats.kendalltau(means, ks)
    #
    # means = df[df.Group=='Pro-Rec.'].groupby(['Coreness'])['Sentiment'].mean()
    # print means
    # ks = range(1, max(g2.vs['coreness'])+1)
    # print ks
    # print statu.stats.kendalltau(means, ks)



    # ---------------------------LIWC features
    # fields = iot.read_fields()
    # trim_files = [f.split('.')[-1] for f in fields]
    # select_f = [
    #     'i', 'we', 'swear', 'negate', 'body', 'health',
    #     'ingest', 'social', 'posemo', 'negemo']
    #
    # for i, f in enumerate(trim_files):
    #     if f in select_f:
    #         # print '------------------------', f
    #
    #         g1 = gt.add_attribute(g1, 'foi', 'fed', 'com', fields[i])
    #         g2 = gt.add_attribute(g2, 'foi', 'fed', 'com', fields[i])
    #         g1c = g1.vs.select(foi_ge=-1)
    #         g2c = g2.vs.select(foi_ge=-1)
    #         # print len(g1c), len(g2c)
    #         g1s = g1.subgraph(g1c)
    #         g2s = g2.subgraph(g2c)
    #
    #         k1, p1 = statu.stats.kendalltau(g1s.vs['centrality'], g1s.vs['foi'])
    #         k2, p2 = statu.stats.kendalltau(g2s.vs['centrality'], g2s.vs['foi'])
    #         print '%s, %.2f%s, %.3f, %.2f%s, %.3f' %(f, k1, mark_pvalue(p1), p1, k2, mark_pvalue(p2), p2)
    #
    #         # g1data = []
    #         # for v in g1s.vs:
    #         #     for core in range(1, v['coreness'] + 1):
    #         #         g1data.append([v['foi'], core, 'Pro-ED'])
    #         # g2data = []
    #         # for v in g2s.vs:
    #         #     for core in range(1, v['coreness'] + 1):
    #         #         g2data.append([v['foi'], core, 'Pro-Rec.'])
    #         #
    #         # df = pd.DataFrame(g1data+g2data, columns=['LIWC', 'Coreness', 'Group'])
    #         #
    #         # means = df[df.Group=='Pro-ED'].groupby(['Coreness'])['LIWC'].mean()
    #         # # print means
    #         # ks = range(1, max(g1s.vs['coreness'])+1)
    #         # # print ks
    #         # t1, p1 = statu.stats.kendalltau(means, ks)
    #         #
    #         # means = df[df.Group=='Pro-Rec.'].groupby(['Coreness'])['LIWC'].mean()
    #         # # print means
    #         # ks = range(1, max(g2.vs['coreness'])+1)
    #         # # print ks
    #         # t2, p2 = statu.stats.kendalltau(means, ks)
    #         # if p1<0.5 and p2<0.5:
    #         #     print '%.2f, %.2f, %.2f, %.2f' %(t1, p1, t2, p2)
    #         #     # sns.factorplot(x='Coreness', y='LIWC', hue="Group", data=df,
    #         #     #                size=10, palette={"Pro-ED": "r",
    #         #     #                                  "Pro-Rec.": "g"
    #         #     #                                  }, legend=False, markers=['o', '^'])
    #         #     # plt.legend(loc='best')
    #         #     # plt.xlabel(r'$k$')
    #         #     # plt.ylabel(f.upper() + r' of $k$-core Users')
    #         #     # plt.show()


def sentiment_injection(netfilename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    g = gt.Graph.Read_GraphML(netfilename)
    cl1 = g.vs.select(cluster=0)
    cl2 = g.vs.select(cluster=1)
    g1 = g.subgraph(cl1)
    g2 = g.subgraph(cl2)
    gt.net_stat(g1)
    gt.net_stat(g2)
    # g1 = gt.giant_component(g1)
    # g2 = gt.giant_component(g2)
    # gt.net_stat(g1)
    # gt.net_stat(g2)

    ped = set(iot.read_ed_pro_hashtags())
    pre = set(iot.read_ed_recovery_hashtags())

    edgesi = g.es.select(_between = (g.vs.select(name_in=g1.vs['name']), g.vs.select(name_in=g2.vs['name'])))
    print len(edgesi)

    user1 = set([int(uid) for uid in g1.vs['name']])
    user2 = set([int(uid) for uid in g2.vs['name']])
    allset = user1.union(user2)
    print len(user1), len(user2), len(allset)

    netdb = dbt.db_connect_col('fed', 'bnet_ed_tag')
    timedb = dbt.db_connect_col('fed', 'ed_tag')
    for link in netdb.find({'type': {'$in': [2, 3]}}):
        if (link['id0'] in allset) and (link['id1'] in allset) :
            id0 = link['id0']
            id1 = link['id1']
            tweet = timedb.find_one({'id': link['statusid']})

            hashtags = tweet['entities']['hashtags']
            hash_set = set()
            for hash in hashtags:
                hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
            pred_sub = hash_set.intersection(ped)
            prec_sub = hash_set.intersection(pre)
            remain = hash_set - pred_sub - prec_sub

            text = tweet['text'].encode('utf8')
            text = rtgrex.sub('', text)
            text = mgrex.sub('', text)
            text = hgrex.sub('', text)
            text = ugrex.sub('', text)
            words = text.split()
            u1l, u2l = 1, 1
            if id0 in user1:
                u1l = 0
            if id1 in user1:
                u2l = 0
            elif id1 in user2:
                u2l = 1
            else:
                u2l = 2
            if len(words) > 0:
                print '%d \t %d \t %d \t %d \t %d \t %s \t -1:%s \t 1:%s \t 0:%s' % (link['statusid'],
                                                                                     id0, u1l, id1, u2l, ' '.join(words),
                                                                                     ' '.join(list(pred_sub)),
                                                                                     ' '.join(list(prec_sub)),
                                                                                     ' '.join(list(remain)))


def analysis_net_sentiments(file='net-tweet.txt'):
    '''Plot sentiment distribution'''
    data = []
    users = {(0, 0): [],
            (0, 1): [],
            (0, 2): [],
            (1, 0): [],
            (1, 1): [],
            (1, 2): [],
                }
    all_tweets, both_tweets = 0, 0
    with open(file, 'r') as fo:
        for line in fo.readlines():
            all_tweets += 1
            tokens = line.strip().split('\t')
            sentiment = int(tokens[-1])
            source_uid = int(tokens[1])
            source = int(tokens[2])
            target_uid = int(tokens[3])
            target = int(tokens[4])
            ped = tokens[6]
            prec = tokens[7]
            # if len(ped)>3:
            #     c += 1
            # if len(prec)>2:
            #     c += 1
            if target < 2:
                data.append([source, target, sentiment])
                users[(source, target)].append(source_uid)
            data.append([source, 2, sentiment])
            users[(source, 2)].append(source_uid)
    df = pd.DataFrame(data, columns=['Source', 'Target', 'Sentiment'])
    # print df
    def mean_std(list):
        return [np.mean(list), np.std(list)]
    amean, astd = mean_std(df[(df.Source==0) & (df.Target==2)]['Sentiment'])
    bmean, bstd = mean_std(df[(df.Source==1) & (df.Target==2)]['Sentiment'])
    print 'Means of all clusters ', amean, astd, bmean, bstd
    # Change abosulate value to z-sore.
    data2 = []
    for index, row in df.iterrows():
        if row['Source'] == 0:
            m, st = amean, astd
        else:
            m, st = bmean, bstd
        if row.Target != 2:
            data2.append([row['Source'], row['Target'], (float(row['Sentiment']-m))/st])
        # data2.append([row['Source'], row['Target'], row['Sentiment']])
    df = pd.DataFrame(data2, columns=['Source', 'Target', 'Sentiment'])
    #---------------------------------

    # def mean_std_ci(list):
    #     cis = bootstrap.ci(data=list, statfunction=scipy.mean, n_samples=1000)
    #     return [np.mean(list), np.std(list), cis[0], cis[1]]
    #
    # m00, sd00, ci100, ci200 = mean_std_ci(df[(df.Source==0) & (df.Target==0)]['Sentiment'])
    # m01, sd01, ci101, ci201 = mean_std_ci(df[(df.Source==0) & (df.Target==1)]['Sentiment'])
    # m10, sd10, ci110, ci210 = mean_std_ci(df[(df.Source==1) & (df.Target==0)]['Sentiment'])
    # m11, sd11, ci111, ci211 = mean_std_ci(df[(df.Source==1) & (df.Target==1)]['Sentiment'])
    # print m00, sd00, ci100, ci200
    # print m01, sd01, ci101, ci201
    # print m10, sd10, ci110, ci210
    # print m11, sd11, ci111, ci211
    # g = gt.Graph([(0,0), (0,1), (1,0), (1,1)], directed=True)
    # g.vs["name"] = ["Pro-ED", "Pro-Rec."]
    # g.vs["baseline"] = [amean, astd]
    # g.es["senti"] = [str(round(m00, 3)), str(round(m01, 3)), str(round(m10, 3)), str(round(m11, 3))]
    # g.es["weight"] = [(round(m00, 3))+1, (round(m01, 3))+1, (round(m10, 3))+1, (round(m11, 3))+1]
    # gt.summary(g)
    # g.write_graphml('inter-sen.graphml')


    sa = len(df[(df.Source==0)])
    sb = len(df[(df.Source==1)])
    aa = len(df[(df.Source==0) & (df.Target==0)])
    ab = len(df[(df.Source==0) & (df.Target==1)])
    ba = len(df[(df.Source==1) & (df.Target==0)])
    bb = len(df[(df.Source==1) & (df.Target==1)])
    print statu.utest(df[(df.Source==0) & (df.Target==0)]['Sentiment'], df[(df.Source==0) & (df.Target==1)]['Sentiment'])
    print statu.utest(df[(df.Source==1) & (df.Target==0)]['Sentiment'], df[(df.Source==1) & (df.Target==1)]['Sentiment'])
    print statu.utest(df[(df.Source==0) & (df.Target==2)]['Sentiment'], df[(df.Source==1) & (df.Target==2)]['Sentiment'])

    print sa, sb, aa, ab, ba, bb
    # dat.append(['Source: Pro-ED', 'Target: Pro-ED', float(aa)/sa])
    # dat.append(['Source: Pro-ED', 'Target: Pro-Rec.', float(ab)/sa])
    # dat.append(['Source: Pro-Rec.', 'Target: Pro-Rec.', float(bb)/sb])
    # dat.append(['Source: Pro-Rec.', 'Target: Pro-ED', float(ba)/sb])

    dat = []
    dat.append(['Source: Pro-ED', 'common', float(aa)/sa])
    dat.append(['Source: Pro-ED', 'inter', float(ab)/sa])
    dat.append(['Source: Pro-Rec.', 'common', float(bb)/sb])
    dat.append(['Source: Pro-Rec.', 'inter', float(ba)/sb])

    pro = pd.DataFrame(dat, columns=['Source', 'Target', 'Proportion'])

    # fig, axs = plt.subplots(ncols=2)
    plu.plot_config()
    g = sns.factorplot(x="Source", y="Proportion", hue="Target", data=pro,
                       kind="bar", legend=False,
                       # palette={"common": "#e9a3c9", "inter": "#a1d76a"}
                       )
    # g.set_xticklabels(["Source: Pro-ED", "Source: Pro-Rec."])
    g.set_xticklabels([r'$L^{ED}_\circlearrowright \quad L^{ED}_\curvearrowright$',
                       r'$L^{Rec}_\circlearrowright \quad L^{Rec}_\curvearrowright$'])
    g.set_ylabels('Link Proportion')
    g.set_xlabels('')
    annots = [aa, bb, ab, ba]
    hatches = ['/','/','\\','\\']
    colors = ["#e9a3c9","#a1d76a","#e9a3c9","#a1d76a"]

    ax=g.ax #annotate axis = seaborn axis
    for i, p in enumerate(ax.patches):
        ax.annotate("{:,}".format(annots[i]), (p.get_x() + p.get_width() / 2., p.get_height()),
             ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
             textcoords='offset points')
        p.set_hatch(hatches[i])
        p.set_fc(colors[i])

    # plt.legend(loc='best')
    plt.show()

    'User proportation'
    user_net = gt.Graph.Read_GraphML('data/communication-only-fed-filter-hashtag-cluster.graphml')
    gt.summary(user_net)
    cluster1 = user_net.subgraph(user_net.vs(cluster=0))
    cluster2 = user_net.subgraph(user_net.vs(cluster=1))
    cluster1_usize = len(cluster1.vs)
    cluster2_usize = len(cluster2.vs)
    print cluster1_usize, cluster2_usize
    clist = [len(set(users[(0,0)])),
             len(set(users[(1,1)])),
             len(set(users[(0,1)])),
             len(set(users[(1,0)])),
             ]
    print clist
    dat = [[0, 0,float(len(set(users[(0,0)])))/cluster1_usize],
           [0, 1,float(len(set(users[(0,1)])))/cluster1_usize],
           [1, 1,float(len(set(users[(1,0)])))/cluster2_usize],
           [1, 0,float(len(set(users[(1,1)])))/cluster2_usize]]
    pro = pd.DataFrame(dat, columns=['Source', 'Target', 'Proportion'])

    pro['Source'] = pro['Source'].map({0: 'Source: Pro-ED', 1: 'Source: Pro-Rec.'})
    pro['Target'] = pro['Target'].map({0: 'common', 1: 'inter'})

    g = sns.factorplot(x="Source", y="Proportion", hue="Target", data=pro,
                       kind="bar", legend=False,
                       # palette={"Target: Pro-ED": "#e9a3c9", "Target: Pro-Rec.": "#a1d76a"}
                       )
    g.set_xticklabels([r'$U^{ED}_\circlearrowright \quad U^{ED}_\curvearrowright$',
                       r'$U^{Rec}_\circlearrowright \quad U^{Rec}_\curvearrowright$'])
    g.set_ylabels('User Proportion')
    g.set_xlabels('')
    annots = clist
    colors = ["#e9a3c9","#a1d76a","#e9a3c9","#a1d76a"]

    ax=g.ax #annotate axis = seaborn axis
    for i, p in enumerate(ax.patches):
        ax.annotate("{:,}".format(annots[i]), (p.get_x() + p.get_width() / 2., p.get_height()),
             ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
             textcoords='offset points')
        p.set_hatch(hatches[i])
        p.set_fc(colors[i])

    # plt.legend(loc='best')
    plt.show()


    'sentiment '

    annots = [np.mean(df[(df.Source==0) & (df.Target==0)]['Sentiment']),
                np.mean(df[(df.Source==1) & (df.Target==0)]['Sentiment']),
                np.mean(df[(df.Source==0) & (df.Target==1)]['Sentiment']),
              np.mean(df[(df.Source==1) & (df.Target==1)]['Sentiment'])
              ]
    print annots

    df['Target'] = np.where((df['Source']==df['Target']), 0, 1)
    df['Source'] = df['Source'].map({0: 'Source: Pro-ED', 1: 'Source: Pro-Rec.'})

    # df['Target'] = df['Target'][].map({0: 'Target: Pro-ED', 1: 'Target: Pro-Rec.'})

    # plu.plot_config()
    g = sns.factorplot(x="Source", y="Sentiment", hue="Target", data=df,
                       kind="bar", legend=False,
                       # palette={"Target: Pro-ED": "#e9a3c9", "Target: Pro-Rec.": "#a1d76a"}
                       )
    ax=g.ax #annotate axis = seaborn axis
    for i, p in enumerate(ax.patches):
        # ax.annotate("%.3f" %(annots[i]), (p.get_x() + p.get_width() / 2., p.get_height() if p.get_y()>=0 else -0.1-p.get_height()),
        #      ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
        #      textcoords='offset points')
        p.set_hatch(hatches[i])
        p.set_fc(colors[i])
    g.set_xticklabels([r'$\langle S^{ED}_\circlearrowright \rangle$ $\quad$ $\langle S^{ED}_\curvearrowright \rangle$',
                       r'$\langle S^{Rec}_\circlearrowright \rangle$ $\quad$ $\langle S^{Rec}_\curvearrowright \rangle$'])
    g.set_ylabels('Relative Sentiment')
    g.set_xlabels('')
    # plt.legend(loc='best')
    plt.show()



def load_scale_data(file_path, multilabeltf=False):
    X, y = load_svmlight_file(file_path, multilabel=multilabeltf)
    X = X.toarray()
    # print X[:, 0]
    # print X[:, 10]
    # print X[:, 21]
    # X = preprocessing.scale(X)
    # min_max_scaler = preprocessing.MinMaxScaler()
    # X = min_max_scaler.fit_transform(X_dentise)
    if multilabeltf == True:
        y = preprocessing.MultiLabelBinarizer().fit_transform(y)
    return (X, y)


def centrality_regresion(netfilename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    # Data for regression on centrality based on liwc features

    #networks
    g = gt.Graph.Read_GraphML(netfilename)
    cl1 = g.vs.select(cluster=0)
    cl2 = g.vs.select(cluster=1)
    g1 = g.subgraph(cl1)
    g2 = g.subgraph(cl2)
    gt.net_stat(g1)
    gt.net_stat(g2)
    uidsmap = dict(zip([(uid) for uid in g.vs['name']], range(len(g.vs))))
    # g1 = gt.giant_component(g1)
    # g2 = gt.giant_component(g2)
    # gt.net_stat(g1)
    # gt.net_stat(g2)

    # pagerank = dict(zip(g1.vs['name'] + g2.vs['name'], g1.pagerank(weights='weight') + g2.pagerank(weights='weight')))
    # author = dict(zip(g1.vs['name'] + g2.vs['name'], g1.authority_score(weights='weight') + g2.authority_score(weights='weight')))
    # hub = dict(zip(g1.vs['name'] + g2.vs['name'], g1.hub_score(weights='weight') + g2.hub_score(weights='weight')))

    # ------------------------Read sentiments
    user_ped, user_prec, user_tweet, user_sentiment = {}, {}, {}, {}
    with open('data/all-tweet.txt', 'r') as fo:
        for line in fo.readlines():
            tokens = line.strip().split('\t')
            uid = tokens[1]
            count = user_tweet.get(uid, 0)
            user_tweet[uid] = count + 1
            sentiment = float(tokens[-1])
            sents = user_sentiment.get(uid, [])
            sents.append(sentiment)
            user_sentiment[uid] = sents
            ped = tokens[4]
            prec = tokens[5]
            if len(ped)>3:
                sents = user_ped.get(uid, [])
                sents.append(sentiment)
                user_ped[uid] = sents
            if len(prec)>2:
                sents = user_prec.get(uid, [])
                sents.append(sentiment)
                user_prec[uid] = sents

    user_ped_mean = [np.sum(user_ped[uid]) for uid in user_ped.keys()]
    user_prec_mean = [np.sum(user_prec[uid]) for uid in user_prec.keys()]
    prostr = dict(zip(user_ped.keys()+user_prec.keys(), user_ped_mean+user_prec_mean))

    select_f = ['engage.friend_count', 'engage.status_count', 'engage.follower_count',
        'engage.friends_day', 'engage.statuses_day', 'engage.followers_day',
        'behavior.retweet_pro', 'behavior.dmention_pro', 'behavior.reply_pro', 'behavior.reply_div', 'behavior.mention_div', 'behavior.retweet_div','timeline_count',
        'liwc_anal.result.i', 'liwc_anal.result.we', 'liwc_anal.result.swear',
        'liwc_anal.result.negate', 'liwc_anal.result.body', 'liwc_anal.result.health',
        'liwc_anal.result.ingest', 'liwc_anal.result.social', 'liwc_anal.result.posemo', 'liwc_anal.result.negemo']
    trim_f = [f.split('.')[-1] for f in select_f]
    data = []
    com = dbt.db_connect_col('fed', 'com')
    for i, uids in enumerate([g1.vs['name'], g2.vs['name']]):
        for uid in uids:
            # vector = [i, uidsmap[uid], prostr.get(uid, 0), pagerank[uid], author[uid], hub[uid]]
            vector = [i, uid, uidsmap[uid], prostr.get(uid, 0)]
            user = com.find_one({'id': int(uid)})
            vector += iot.get_fields_one_doc(user, select_f)
            data.append(vector)
    # df = pd.DataFrame(data, columns=['cluster', 'uid', 'prostr', 'pagerank', 'author', 'hub'] + trim_f)
    df = pd.DataFrame(data, columns=['cluster', 'uid', 'uidmap', 'prostr'] + trim_f)
    # df.to_csv('centrality-features.csv', index=False)
    df.to_csv('users-features.csv', index=False)

def robust_reg(ped, name):
    # rubost linear regresson
    ped['constant'] = 1
    pedt = sm.RLM(ped.pagerank, ped[[name, 'friend_count', 'status_count',
                                     'follower_count', 'dmention_pro', 'reply_pro', 'timeline_count', 'constant']])
    ped_results = pedt.fit()
    return ped_results


def robust_regression(filepa='centrality-features.csv'):
    data = pd.read_csv(filepa)
    # Normalized by the total number of tweets
    data['prostr'] = data['prostr'] / data['timeline_count']
    ped = data[data.cluster==0]
    rec = data[data.cluster==1]
    names = ['body', 'ingest', 'health', 'i', 'we', 'social', 'swear', 'negate', 'posemo', 'negemo', 'prostr']
    # ped['pagerank'] *= 100
    res = []
    for name in names:
        ped_results = robust_reg(ped, name)
        rec_results = robust_reg(rec, name)
        # print(ped_results.summary())
        # print(rec_results.summary())
        pede = ped_results.params[0]
        rece = rec_results.params[0]
        pedci = ped_results.conf_int()
        recci = rec_results.conf_int()
        res.append(['ed', pede, pedci[0][0], pedci[1][0], name, ped_results.bse[0], ped_results.pvalues[0]])
        res.append(['rec', rece, recci[0][0], recci[1][0], name, rec_results.bse[0], rec_results.pvalues[0]])
    df = pd.DataFrame(res, columns=['group', 'coef', 'low', 'high', 'name', 'ste', 'p'])
    print df


    plu.plot_config()
    sns.set_style("ticks")
    ###pro-ED users
    d = df[df.group=='ed']
    print d
    # Two subplots, the axes array is 1-d
    f, axarr = plt.subplots(2, sharex=True)
    (plotlines, caps, _) = axarr[0].errorbar(range(len(d.name)), d.coef, yerr=[d.ste*1.96, d.ste*1.96],
                     fmt='o',  markersize='15',elinewidth=5, mfc='#e9a3c9', ecolor='#e9a3c9', label="Pro-ED Users")
    axarr[0].axhline(0, color='black', linestyle='--')
    axarr[0].set_yticks(np.arange(-0.0006, 0.0009, 0.0006))


    ps = d.p.tolist()
    his = d.high.tolist()
    los = d.low.tolist()
    cofs = d.coef.tolist()
    for i in (range(len(d.name))):
        if (ps[i]) < 0.05:
            axarr[0].annotate("*", xy=(i, his[i]-0.0001 if cofs[i]>0 else los[i]-0.0003),
             ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
             textcoords='offset points')

    axarr[0].set_ylabel('Pro-ED')
    # axarr[0].yaxis.label.set_position((0, -0.12))
    axarr[0].grid(False)
    # axarr[0].spines['bottom'].set_visible(False)
    # handles, labels = axarr[0].get_legend_handles_labels()
    # handles = [h[0] for h in handles]
    # axarr[0].legend(handles, labels, loc='upper right',numpoints=1, frameon=True)

    ## pro-recovery users
    d = df[df.group=='rec']
    print d
    (plotlines, caps, _) = axarr[1].errorbar(range(len(d.name)), d.coef, yerr=[d.ste*1.96, d.ste*1.96],
                     fmt='s', markersize='15',elinewidth=5, mfc='#a1d76a', ecolor='#a1d76a', label="Pro-Rec. Users")
    axarr[1].axhline(0, color='black', linestyle='--')
    axarr[1].set_yticks(np.arange(-0.06, 0.06, 0.03))
    axarr[1].set_ylabel('Pro-Rec.')
    # handles, labels = axarr[1].get_legend_handles_labels()
    # handles = [h[0] for h in handles]
    # axarr[1].legend(handles, labels, loc='lower right', numpoints=1, frameon=True)
    axarr[1].set_xlim(-1, len(names))
    axarr[1].grid(False)
    ps = d.p.tolist()
    his = d.high.tolist()
    los = d.low.tolist()
    cofs = d.coef.tolist()
    for i in (range(len(d.name))):
        if (ps[i]) < 0.05:
            axarr[1].annotate("*", xy=(i, his[i]-0.005 if cofs[i]>0 else los[i]-0.02),
             ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
             textcoords='offset points')

    plt.xticks(range(len(names)), [name.title() for name in names], rotation=30)
    # axarr[1].spines['bottom'].set_visible(False)
    # plt.tight_layout()
    sns.despine()
    plt.show()



    # d = df[df.group=='ed']
    # print d
    # g = plt.errorbar(range(len(d.name)), d.coef, yerr=d.ste*1.96,
    #                  fmt='o', markersize='10', mfc='#e9a3c9', ecolor='#e9a3c9', label="Pro-ED Users")
    # plt.xticks(range(len(names)), names, rotation='vertical')
    # plt.yticks(np.arange(-0.0004, 0.0009, 0.0004))
    # plt.grid(False)
    # plt.axhline(0, color='black', linestyle='--')
    # plt.xlim(-1, len(names))
    # plt.ylabel('Coefficient')
    # handles, labels = plt.gca().get_legend_handles_labels()
    # # remove the errorbars
    # handles = [h[0] for h in handles]
    # # use them in the legend
    # plt.legend(handles, labels, loc='upper right',numpoints=1, frameon=True)
    # # plt.legend(loc=0, frameon=True)
    # plt.show()


    # d = df[df.group=='rec']
    # print d
    # print d.name
    # print d.coef
    # print d.ste
    # g = plt.errorbar(range(len(d.name)), d.coef, yerr=[d.ste*1.96, d.ste*1.96],
    #                  fmt='o', markersize='10',
    #                  mfc='#a1d76a', ecolor='#a1d76a', label="Pro-Rec Users"
    #                  )
    # plt.xticks(range(len(names)), names, rotation='vertical')
    # # plt.yticks(np.arange(-0.0004, 0.0009, 0.0004))
    # plt.grid(False)
    # plt.axhline(0, color='black', linestyle='--')
    # plt.xlim(-1, len(names))
    # plt.ylabel('Coefficient')
    # plt.show()


def data_validataion(netfilename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    # import random
    # g = gt.Graph.Read_GraphML(netfilename)
    # cl1 = g.vs.select(cluster=0)
    # cl2 = g.vs.select(cluster=1)
    # cl1names = cl1['name']
    # cl2names = cl2['name']
    # print len(cl2names)
    # com = dbt.db_connect_col('fed', 'com')
    # # for uid in cl1names[:50]:
    # #     print uid
    # # print '-------------------------------------'
    # random.shuffle(cl2names)
    # for uid in cl2names[:50]:
    #     user = com.find_one({'id': int(uid)})
    #     print user['screen_name']

    trues, preds = [], []
    c = 0
    with open('annotation/labels.txt', 'r') as fo:
        for i, line in enumerate(fo.readlines()):
            tokens = line.strip().split('\t')
            if i < 50:
                t = 0
            else:
                t = 1
            if tokens[-1] == 'ED':
                p = 0
                trues.append(t)
                preds.append(p)
            elif tokens[-1] == 'REC':
                p = 1
                trues.append(t)
                preds.append(p)
            else:
                if i < 50:
                    c += 1
    from sklearn import metrics
    print len(trues)
    print len(preds)
    print c
    print metrics.cohen_kappa_score(trues, preds)


def out_tweet_ids(netfilename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    g = gt.Graph.Read_GraphML(netfilename)
    gt.summary(g)
    uids = dict(zip([int(uid) for uid in g.vs['name']], range(len(g.vs))))
    times = dbt.db_connect_col('fed', 'ed_tag')
    for tweet in times.find():
        if tweet['user']['id'] in uids:
            print uids[tweet['user']['id']], '\t', tweet['id']

    # data = []
    # uids = dict(zip([int(uid) for uid in g.vs['name']], range(len(g.vs))))
    # print len(uids)
    # times = dbt.db_connect_col('fed', 'ed_tag')
    # tid = 0
    # for tweet in times.find():
    #     if tweet['user']['id'] in uids:
    #         tid = tid + 1
    #         uid = uids[tweet['user']['id']]
    #         hashtags = tweet['entities']['hashtags']
    #         hash_set = set()
    #         for hash in hashtags:
    #             hash_set.add(hash['text'].encode('utf-8').lower().replace('_', '').replace('-', ''))
    #         hash_set = ', '.join(list(hash_set))
    #         retweet = False
    #         if ('retweeted_status' in tweet):
    #             retweet = True
    #         mentions = []
    #         if retweet == False:
    #             for mention in tweet['entities']['user_mentions']:
    #                 if mention['id'] in uids:
    #                     mentions.append(uids[mention['id']])
    #         # mentions = ', '.join([str(mid) for mid in set(mentions)])
    #         # data.append([tid, uid, retweet, hash_set, mentions])
    #         if len(mentions) > 0:
    #             for mention in mentions:
    #                 data.append([uid, mention])
    #         #     data.append([uid, mentions])
    #         # ['tweet_id', 'author_id', 'retweet', 'hashtags', 'mentions']
    # df = pd.DataFrame(data, columns=['tweet_id', 'mentions'])
    # df.to_csv('data/tweets.csv')


def out_graph(netfilename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    g = gt.Graph.Read_GraphML(netfilename)
    gt.summary(g)
    g.vs['name'] = range(len(g.vs))
    g.write_graphml('data/newgraph.graphml')

def read_graph(filename='data/linktweets.txt'):
    name_map, edges = {}, set()
    with open(filename, 'r') as fo:
        for line in fo.readlines():
            ids = line.split(',')
            n1 = ids[0]
            n2 = ids[1]

            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            n2id = name_map.get(n2, len(name_map))
            name_map[n2] = n2id
            edges.add((n1id, n2id))
        g = gt.Graph(len(name_map), directed=True)
        g.vs["name"] = list(sorted(name_map, key=name_map.get))
        g.add_edges(list(edges))
        g.es["weight"] = 1
        gt.summary(g)
        g.write_graphml('data/regraph.graphml')


if __name__ == '__main__':
    # net_attr()
    # out_graph()
    # out_tweet_ids()
    # read_graph()
    # regression()
    # assortative_test()
    # interaction_ratio()
    # prominence()
    # liwc_sim()
    # compare_liwc()
    # sentiment_quanti()
    # prelevence()
    # analysis_sentiments('data/all-tweet.txt')
    # compare_in_out_degree()
    # compare_in_out_degree_allconnection()
    # split_in_out_degree()
    # core_analysis()
    # sentiment_injection() #net-tweet.txt
    # analysis_net_sentiments()
    centrality_regresion()
    # robust_regression()
    # data_validataion()
