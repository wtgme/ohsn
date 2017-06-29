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
from scipy.stats import ttest_ind
import ohsn.sentiment.senstrength as sentre
import re
import statsmodels.stats.api as sms
import powerlaw

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
    # # counting how popular each type of content overall
    # prelence.pick for all tweets and retweets
    # tweet-prelence.pick only counting tweets to avoid duplicated counting
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

    # df = pickle.load(open('data/tweet-prelence.pick', 'r'))
    # df.rename(columns={'Cluster': 'Content'
    #                    },
    #           inplace=True)
    # plu.plot_config()
    # g = sns.factorplot(x="Action", y="Count", hue="Content", data=df, kind="bar", legend=True, palette={"Pro-ED": "r", "Pro-Rec.": "g"})
    # plt.show()




def sentiment_quanti(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    # tweet.txt: only contain tweets that have proed or pro-recovery hashtags, not retweets
    # retweet.txt: contain tweets and retweets that have proed or pro-recovery hashtags
    # all-tweet.txt: contain all tweets and retweets that have proed or pro-recovery and other hashtags
    # only-tweet.txt: contain only tweets that have pro-ed, pro-rec or other tags

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
                        print str(i)+'\t'+ str(uid)+'\t'+ ' '.join(words) + \
                              '\t'+ '-1:'+' '.join(list(pred_sub)) + \
                              '\t'+ '1:'+' '.join(list(prec_sub)) + \
                              '\t' + '0:'+' '.join(list(remain))

def analysis_sentiments(file='tweets.txt'):
    # AB, AA, BB, BA = [], [], [], []
    data = []
    all_tweets, both_tweets = 0, 0
    with open(file, 'r') as fo:
        for line in fo.readlines():
            all_tweets += 1
            tokens = line.strip().split('\t')
            label = int(tokens[0])
            sentiment = int(tokens[-1])
            ped = tokens[3]
            prec = tokens[4]
            c = 0
            if len(ped)>3:
                c += 1
            if len(prec)>2:
                c += 1

            if c==1:
                if label==0 and len(ped)>3:
                    # AA.append(float(sentiment)/c)
                    data.append(['A', 0, float(sentiment)/c])
                if label==0 and len(prec)>2:
                    # AB.append(float(sentiment)/c)
                    data.append(['A', 1, float(sentiment)/c])
                if label==1 and len(ped)>3:
                    # BA.append(float(sentiment)/c)
                    data.append(['B', 0, float(sentiment)/c])
                if label == 1 and len(prec)>2:
                    # BB.append(float(sentiment)/c)
                    data.append(['B', 1, float(sentiment)/c])
            elif c == 2:
                both_tweets += 1
                if label == 0:
                    data.append(['A', 2, float(sentiment)])
                if label == 1:
                    data.append(['B', 2, float(sentiment)])
            else:
                if label == 0:
                    data.append(['A', 3, float(sentiment)])
                if label == 1:
                    data.append(['B', 3, float(sentiment)])
            # add average for all
            if label == 0:
                    data.append(['A', 4, float(sentiment)])
            if label == 1:
                data.append(['B', 4, float(sentiment)])

    print both_tweets, all_tweets, float(both_tweets/all_tweets)
    df = pd.DataFrame(data, columns=['Cluster', 'Topic', 'Sentiment'])
    # print np.mean(df[(df['Cluster']=='A')&(df['Topic']==1)]['Sentiment'])

    #change values in colcumn
    df['Cluster'] = df['Cluster'].map({'A': 'Pro-ED Clust.', 'B': 'Pro-Rec. Clust.'})

    plu.plot_config()
    g = sns.factorplot(x="Topic", y="Sentiment", hue="Cluster", data=df, kind="bar", legend=False, palette={"Pro-ED Clust.": "r", "Pro-Rec. Clust.": "g"})
    g.set_xticklabels(["Pro-ED", "Pro-Rec.", "Mixed", "Unspecified", "All"])
    plt.legend(loc='best')
    # sns.distplot(AA, hist=False, kde_kws={"color": "r", "lw": 2, "marker": 'o'}, label='A-A ($\mu=%0.2f$)' % (np.mean(AA)))
    # sns.distplot(BB, hist=False, kde_kws={"color": "g", "lw": 2, "marker": 'o'}, label='B-B ($\mu=%0.2f$)' % (np.mean(BB)))
    # sns.distplot(AB, hist=False, kde_kws={"color": "y", "lw": 2, "marker": 's'}, label='A-B ($\mu=%0.2f$)' % (np.mean(AB)))
    # sns.distplot(BA, hist=False, kde_kws={"color": "b", "lw": 2, "marker": 's'}, label='B-A ($\mu=%0.2f$)' % (np.mean(BA)))
    plt.show()
    plt.clf()

    df['Cluster'] = df['Cluster'].map({'Pro-ED Clust.': 'A', 'Pro-Rec. Clust.': 'B'})
    dat = []
    A = len(df[df.Cluster=='A'])
    B = len(df[df.Cluster=='B'])
    print A, B
    AAc = len(df[(df.Cluster=='A') & (df.Topic==0)])
    dat.append(['A', 0, float(AAc)/A])
    ABc = len(df[(df.Cluster=='A') & (df.Topic==1)])
    dat.append(['A', 1, float(ABc)/A])
    ACc = len(df[(df.Cluster=='A') & (df.Topic==2)])
    dat.append(['A', 2, float(ACc)/A])
    ADc = len(df[(df.Cluster=='A') & (df.Topic==3)])
    dat.append(['A', 3, float(ADc)/A])

    BAc = len(df[(df.Cluster=='B') & (df.Topic==0)])
    dat.append(['B', 0, float(BAc)/B])
    BBc = len(df[(df.Cluster=='B') & (df.Topic==1)])
    dat.append(['B', 1, float(BBc)/B])
    BCc = len(df[(df.Cluster=='B') & (df.Topic==2)])
    dat.append(['B', 2, float(BCc)/B])
    BDc = len(df[(df.Cluster=='B') & (df.Topic==3)])
    dat.append(['B', 3, float(BDc)/B])


    pro = pd.DataFrame(dat, columns=['Cluster', 'Topic', 'Proportion'])
    pro['Cluster'] = pro['Cluster'].map({'A': 'Pro-ED Clust.', 'B': 'Pro-Rec. Clust.'})
    print pro
    plu.plot_config()
    g = sns.factorplot(x="Topic", y="Proportion", hue="Cluster", legend=False, kind="bar", data=pro, palette={"Pro-ED Clust.": "r", "Pro-Rec. Clust.": "g"})
    g.set_xticklabels(["Pro-ED", "Pro-Rec.","Mixed", "Unspecified"])
    plt.legend(loc='best')
    plt.show()


    print statu.ttest(df[(df.Cluster=='A') & (df.Topic==0)]['Sentiment'], df[(df.Cluster=='B') & (df.Topic==0)]['Sentiment'])
    print statu.ttest(df[(df.Cluster=='A') & (df.Topic==1)]['Sentiment'], df[(df.Cluster=='B') & (df.Topic==1)]['Sentiment'])
    print statu.ttest(df[(df.Cluster=='A') & (df.Topic==2)]['Sentiment'], df[(df.Cluster=='B') & (df.Topic==2)]['Sentiment'])
    print statu.ttest(df[(df.Cluster=='A') & (df.Topic==3)]['Sentiment'], df[(df.Cluster=='B') & (df.Topic==3)]['Sentiment'])



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
                # 'friends_day', 'statuses_day', 'followers_day',
        'retweet_pro',
        # 'dmention_pro', 'reply_pro',
        # 'hashtag_pro',
        'url_pro',
                'retweet_div',
        # 'reply_div',
        'mention_div',
                'i', 'we', 'swear', 'negate', 'body', 'health',
                'ingest', 'social', 'posemo', 'negemo']
    indecs = [trim_files.index(f) for f in select_f]
    X = X[:, indecs]
    print X.shape
    # '''Calculate positive emotion ratio'''
    X[:, -2] /= (X[:, -2] + X[:, -1])
    X = X[:, :-1]
    X[:, -1][~np.isfinite(X[:, -1])] = 0
    print X.shape

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

    print statu.ttest(AA, BB)
    print statu.ttest(AA, AB)
    print statu.ttest(AB, BB)

    plu.plot_config()
    sns.distplot(AA, hist=False, kde_kws={"color": "r", "lw": 2, "marker": 'o'}, label='Pro-ED ($\mu=%0.2f$)' % (np.mean(AA)))
    sns.distplot(BB, hist=False, kde_kws={"color": "g", "lw": 2, "marker": 's'}, label='Pro-Rec. ($\mu=%0.2f$)' % (np.mean(BB)))
    sns.distplot(AB, hist=False, kde_kws={"color": "k", "lw": 2, "marker": '^'}, label='Cross-Cluster ($\mu=%0.2f$)' % (np.mean(AB)))
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

def compare_in_out_degree(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    # # Compare the relation between in and out degree in two clustsers of users.
    # g = gt.Graph.Read_GraphML(filename)
    # gt.summary(g)
    #
    # cl1 = g.vs.select(cluster=0)
    # cl2 = g.vs.select(cluster=1)
    # # g1 = g.subgraph(g.vs.select(cluster=0))
    # # g2 = g.subgraph(g.vs.select(cluster=1))
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
    # for i, net in enumerate([cl1, cl2]):
    #     label = ['Pro-ED', 'Pro-Rec.'][i]
    #     for v in net:
    #         sout = sum(g.es.select(_source=v.index)['weight'])
    #         sin = sum(g.es.select(_target=v.index)['weight'])
    #         dout = len(g.es.select(_source=v.index))
    #         din = len(g.es.select(_target=v.index))
    #         data.append([dout, din, sout, sin, label])
    # df = pd.DataFrame(data, columns=['d_out', 'd_in', 's_out', 's_in', 'Cluster'])
    # pickle.dump(df, open('dfed.pick', 'w'))

    df = pickle.load(open('dfed.pick', 'r'))
    plu.plot_config()
    xa, ya = df[df['Cluster']=='Pro-ED']['d_in'], df[df['Cluster']=='Pro-ED']['d_out']
    xb, yb = df[df['Cluster']=='Pro-Rec.']['d_in'], df[df['Cluster']=='Pro-Rec.']['d_out']
    print len(xa), len(ya)
    print len(xa[xa>0]) , len(ya[ya>0]), float(len(xa[xa>0]))/len(xa), float(len(ya[ya>0]))/len(ya)
    print len(xb), len(yb)
    print len(xb[xb>0]) , len(yb[yb>0]), float(len(xb[xb>0]))/len(xb), float(len(yb[yb>0]))/len(yb)


    xas = xa[(xa>0)&(ya>0)]
    yas = ya[(xa>0)&(ya>0)]
    xbs = xb[(xb>0)&(yb>0)]
    ybs = yb[(xb>0)&(yb>0)]

    plu.dependence(xas, yas, 'd', 'in-degree', 'out-degree')


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
    # Compare the relation between in and out degree in two clustsers of users.
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
                # 'friends_day', 'statuses_day', 'followers_day',
        'retweet_pro',
        # 'dmention_pro', 'reply_pro',
        # 'hashtag_pro',
        'url_pro',
                'retweet_div',
        # 'reply_div',
        'mention_div',
                'i', 'we', 'swear', 'negate', 'body', 'health',
                'ingest', 'social', 'posemo', 'negemo']

    indecs = [trim_files.index(f) for f in select_f]
    print indecs
    X = X[:, indecs]

    '''Calculate positive emotion ratio'''
    # print X.shape
    X[:,-2] /= (X[:,-2] + X[:, -1])
    X = X[:, :-1]
    X[:, -1][~np.isfinite(X[:, -1])] = 0

    min_max_scaler = preprocessing.MinMaxScaler()
    X = min_max_scaler.fit_transform(X)

    # X = preprocessing.scale(X)

    print X.shape, y.shape
    Z = np.append(X, y.reshape((len(y), 1)), axis=1)
    df = pd.DataFrame(Z, columns=select_f[:-1] + ['label'])

    df.rename(columns={'friend_count': '#Fr',
                       'status_count': '#T',
                       'follower_count': '#Fo',
                       'friends_day': '#Fr/D',
                       'statuses_day': '#T/D',
                       'followers_day': '#Fo/D',
                       'retweet_pro': '%RT',
                       'url_pro': '%URL',
                       'retweet_div': 'Div(RT)',
                       'reply_div': 'Div(RP)',
                       'mention_div': 'Div(@)',
                       'posemo': 'PER'
                       },
              inplace=True)

    for col in df.columns[:-1]:
        cat1 = df[col][df['label']==0]
        cat2 = df[col][df['label']==1]
        m1, std1, m2, std2, t, p, pm = statu.ttest(cat1, cat2, len(select_f))
        mark = ''
        if pm < 0.05:
            mark = '*'
        if pm < 0.01:
            mark = '**'
        if pm < 0.001:
            mark = '***'
        print "%s, %.2f (%.3f), %.2f (%.3f), %.2f, %.3f %s" %(col, m1, std1, m2, std2, t, p, mark)


    data = pd.melt(df, id_vars=['label'])
    data['label'] = data['label'].map({0.0: 'A', 1.0: 'B'})
    data.columns = ['Cluster', 'Measure', 'Value']
    data['Cluster'] = data['Cluster'].map({'A': 'Pro-ED', 'B': 'Pro-Rec.'})


    plu.plot_config()
    sns.violinplot(x="Measure", y="Value", hue="Cluster", data=data, split=True,
               inner="quart", palette={"Pro-ED": "r", "Pro-Rec.": "g"})
    # sns.boxplot(x="Measure", y="Value", hue="Cluster", data=data,
    #             palette={"A": "r", "B": "g"})
    sns.despine(left=True)
    plt.legend(loc="best")
    plt.show()



if __name__ == '__main__':
    # net_attr()
    # regression()
    # assortative_test()
    # interaction_ratio()
    # prominence()
    # liwc_sim()
    # compare_liwc()
    sentiment_quanti()
    prelevence()
    # analysis_sentiments('all-tweet.txt')
    # compare_in_out_degree()
    # compare_in_out_degree_allconnection()
    # split_in_out_degree()