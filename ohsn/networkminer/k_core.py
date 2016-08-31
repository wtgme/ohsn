# -*- coding: utf-8 -*-
"""
Created on 12:11, 24/08/16

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.graph_util as gt
import ohsn.util.plot_util as pt
import ohsn.util.io_util as iot
import seaborn as sns
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd

def coreness(g):
    # in_coreness = g.shell_index(mode='IN')
    # out_coreness = g.shell_index(mode='OUT')
    '''If directly using ALL parameter, the counted degrees are the sum of
    IN-degrees adn OUT-degrees'''
    g = g.as_undirected(mode="collapse")
    all_coreness = g.shell_index(mode='ALL')

    # # print len(in_coreness), len(out_coreness), len(all_coreness)
    # group_labels = ['In-Coreness', 'Out-Coreness', 'UnDir-Coreness']
    # pt.plot_config()
    #
    # sns.distplot(in_coreness, hist=False, label=group_labels[0])
    # sns.distplot(out_coreness, hist=False, label=group_labels[1])
    # sns.distplot(all_coreness, hist=False, label=group_labels[2])
    # plt.xlim(0, 100)
    # plt.xlabel('Coreness')
    # plt.ylabel('Density')
    # plt.show()


def coreness_features(g):
    g = g.as_undirected(mode="collapse")
    all_coreness = g.shell_index(mode='ALL')
    g.vs['core'] = all_coreness
    fields = iot.read_fields()
    for field in fields:
        gt.add_attribute(g, 'pof', 'fed', 'com', field)
        vlist = g.vs.select(pof_ne=-1000000000.0)['core']
        flist = g.vs.select(pof_ne=-1000000000.0)['pof']
        pt.correlation(vlist, flist, 'K-Core', 'Feature', 'data/corerel/'+field+'.pdf')
        ################Plot Feaure values and K ##########################################
        # mean, std = [], []
        # for index in xrange(min(all_coreness), max(all_coreness)+1):
        #     values = g.vs.select(core_eq=index)['pof']
        #     values = [v for v in values if v!=-1000000000.0]
        #     print len(values)
        #     mean.append(np.mean(values))
        #     std.append(np.std(values))
        # pt.plot_config()
        # sns.set(style="whitegrid")
        # plt.errorbar(range(min(all_coreness), max(all_coreness)+1), mean, yerr=std, ecolor='green')
        # plt.xlabel('K-Core')
        # plt.ylabel('Feature')
        # plt.savefig('data/corer/'+field+'.pdf')
        # plt.clf()
        # plt.close()
        ##########################################################

def k_core_g(g, uset=None):
    g = g.as_undirected(mode="collapse")
    print g.summary()
    index = 1
    stats = []
    print '------------------------------------'
    gc = g.k_core(index)
    while gc.vcount() > 0:
        print index
        print gc.summary()
        # node_n = gc.vcount()
        # edge_m = gc.ecount()
        # density = gc.density()
        # avg_path = gc.average_path_length()
        # components = gc.components()
        # comp_count = len(components)
        # giant_comp = components.giant()
        # giant_comp_r = float(giant_comp.vcount())/node_n
        # cluster_co_global = gc.transitivity_undirected()
        # vset = set(gc.vs["name"])
        # purity = float(len(uset.intersection(vset)))/len(vset)
        # edp = float(len(uset.intersection(vset)))/len(uset)
        if index > 94:
            return gc.vs["name"]
        # stat = [node_n, edge_m, density, avg_path, comp_count, giant_comp_r, cluster_co_global, purity
        #         ]
        # stats.append(stat)
        index += 1
        gc = g.k_core(index)
    # stats = np.array(stats)
    # names = ['#Nodes', '#Edges', 'G-Density', 'Avg-Path', '#Component', 'Giant Component Ratio', 'Transitivity', 'Purity'
    #          ]
    # data = pd.DataFrame(stats, columns=names)
    # data.to_csv('rdata.csv')
    # pt.plot_config()
    # for i in xrange(stats.shape[1]):
    #     plt.clf()
    #     sns.tsplot(data=stats[:,i])
    #     # plt.xlim(0, 100)
    #     plt.xlabel('K-Core')
    #     plt.ylabel(names[i])
    #     plt.show()


def ed_user(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    userlist = []
    for user in com.find():
        userlist.append(user['id_str'])
    return userlist

def verify_core_user(dbname, colname, usetlist):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    for uid in usetlist:
        user = com.find_one({'id': int(uid)})
        if user['level'] != 1:
            print user['screen_name'].encode('utf-8')
        # print uid, user['screen_name'].encode('utf-8'), ' '.join(user['description'].split()).encode('utf-8')


if __name__ == '__main__':
    # g = gt.load_network('fed', 'net')
    # pickle.dump(g, open('data/fedfried.pick', 'w'))
    g = pickle.load(open('data/fedfried.pick', 'r'))
    print g.summary()
    # coreness(g)
    uset = ed_user('fed', 'scom')
    # k_core_g(g, set(uset))
    core_users = k_core_g(g, set(uset))
    verify_core_user('fed', 'com', core_users)
    # coreness_features(g)


