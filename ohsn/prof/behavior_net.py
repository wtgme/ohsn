# -*- coding: utf-8 -*-
"""
Created on 16:53, 26/05/16

@author: wt
Analysis whether a user often retweet one person
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.graph_util as gt
import ohsn.util.db_util as dbt
import pickle
import ohsn.util.io_util as iot
import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt
from content import compore_distribution


def bahavior_net(dbname, comname, bnetname, btype):
    userlist = iot.get_values_one_field(dbname, comname, 'id',
                                        {'timeline_count': {'$gt': 0}})
    return gt.load_all_beh_network(userlist, dbname, bnetname, btype)


def extract_hashtags():
    dbnames = [('fed', 'stimeline'),
               ('random', 'timeline'),
               ('young', 'timeline')]
    with open('data/hashtags.data', 'w') as fw:
        for dbname, timename in dbnames:
            db = dbt.db_connect_no_auth(dbname)
            cols = db[timename]
            for row in cols.find({'$where': "this.entities.hashtags.length>0"}, no_cursor_timeout=True):
                hashtags = row['entities']['hashtags']
                hlist = list()
                for hashtag in hashtags:
                    hlist.append(hashtag['text'].lower())
                fw.write((dbname + '\t' + row['id_str'] + '\t' + row['user']['id_str'] + '\t' + ' '.join(hlist) + '\n').encode('utf-8'))

def entropy(strenths):
    pros = np.asarray(strenths, np.float64)/sum(strenths)
    entropy = stat.entropy(pros)
    return entropy, entropy/np.log(len(strenths))


def hashtag_net():
    dbnames = [('fed', 'stimeline'),
               ('random', 'timeline'),
               ('young', 'timeline')]
    for dbname, timename in dbnames:
        userlist = iot.get_values_one_field(dbname, 'scom', 'id_str',
                                        {'timeline_count': {'$gt': 0}})
        # g = gt.load_user_hashtag_network(dbname, timename)
        # pickle.dump(g, open('data/'+dbname+'_hashtag.pick', 'w'))
        g = pickle.load(open('data/'+dbname+'_hashtag.pick', 'r'))


def netstatis(g, userlist):
    g = g.as_undirected(combine_edges=dict(weight="sum"))

    # node_n = g.vcount()
    # edge_m = g.ecount()
    # degree_mean = np.mean(g.indegree())
    # degree_std = np.std(g.indegree())
    # density = g.density()
    # avg_path = g.average_path_length()
    # components = g.clusters()
    # comp_count = len(components)
    # giant_comp = components.giant()
    # giant_comp_r = float(giant_comp.vcount())/node_n
    # cluster_co_global = g.transitivity_undirected()
    # cluster_co_avg = g.transitivity_avglocal_undirected()
    # assort = g.assortativity_degree(directed=False)


    gnode = g.vs.select()["name"]
    target_nodes = list(set(userlist).intersection(gnode))

    strengths = np.array(g.strength(target_nodes, mode='OUT', loops=False, weights='weight'))
    # maxv, minv = np.percentile(strengths, 97.5), np.percentile(strengths, 2.5)
    maxv, minv = max(strengths), min(strengths)
    index = np.logical_and(strengths >= minv, strengths <= maxv)
    target_nodes = np.asarray(target_nodes, dtype=str)[index]

    degreess = g.degree(target_nodes, mode='OUT', loops=False)
    strengths = g.strength(target_nodes, mode='OUT', loops=False, weights='weight')

    # print target_nodes
    divs = np.array(g.diversity(target_nodes, 'weight'))*np.log(degreess)
    divs[~np.isfinite(divs)] = 0.0

    # print node_n, edge_m, round(degree_mean, 3), round(degree_std, 3), round(density, 3), \
    #     round(avg_path, 3), comp_count, round(giant_comp_r, 3), round(cluster_co_global, 3), \
    #     round(cluster_co_avg, 3), round(assort, 3), \
    # print len(target_nodes), np.mean(degreess), np.std(degreess),\
    # np.mean(strengths), np.std(strengths),\
    #     np.mean(divs), np.std(divs)
    return divs


def plot_diversity():
    N = 4
    edMeans = (2.90, 1.94, 2.06, 2.65)
    edStd =   (1.47, 1.27, 1.24, 1.31)

    rdMeans = (4.39, 3.33, 3.37, 3.85)
    rdStd =   (1.58, 1.53, 1.46, 1.51)

    ygMeans = (3.91, 3.14, 3.35, 4.16)
    ygStd =   (1.51, 1.41, 1.44, 1.64)

    ind = np.arange(N)  # the x locations for the groups
    width = 0.25       # the width of the bars

    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects1 = ax.bar(ind, edMeans, width, color='g', yerr=edStd, hatch='//', edgecolor='black')
    rects2 = ax.bar(ind+width, rdMeans, width, color='b', yerr=rdStd, hatch='.', edgecolor='black')
    rects3 = ax.bar(ind+2*width, ygMeans, width, color='r', yerr=ygStd, hatch='\\\\', edgecolor='black')

    # add some
    ax.set_ylabel('Diversity')
    # ax.set_title('Scores by group and gender')
    ax.set_xticks(ind+1.5*width)
    ax.set_xticklabels( ('Retweet', 'Reply', 'Mention', 'Hashtag') )

    ax.legend( (rects1[0], rects2[0], rects3[0]), ('ED', 'Random', 'Younger'), ncol=6 )

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%.2f'%(height),
                    ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.show()


def diversity_db(dbname, behavior):
    userlist = iot.get_values_one_field(dbname, 'scom', 'id_str',
                                        {'timeline_count': {'$gt': 0}})
    # g = bahavior_net(dbname, 'scom', 'bnet', behavior)
    # pickle.dump(g, open('data/'+dbname+'_'+behavior+'.pick', 'w'))
    # print dbname, behavior
    g = pickle.load(open('data/' + dbname + '_' + behavior + '.pick', 'r'))
    return netstatis(g, userlist)


if __name__ == '__main__':

    dbnames = ['fed', 'random', 'young']
    behaviors = ['retweet', 'reply', 'mention', 'communication', 'all', 'hashtag']
    for behavior in behaviors:
        ed = diversity_db(dbnames[0], behavior)
        rd = diversity_db(dbnames[1], behavior)
        yg = diversity_db(dbnames[2], behavior)
        compore_distribution(behavior, ed, rd, yg)


    ###do hashtag network###
    # hashtag_net()

    # extract_hashtags()

    # plot_diversity()
