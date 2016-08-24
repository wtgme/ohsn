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
import seaborn as sns
import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd

def coreness(g):
    in_coreness = g.shell_index(mode='IN')
    out_coreness = g.shell_index(mode='OUT')
    '''If directly using ALL parameter, the counted degrees are the sum of
    IN-degrees adn OUT-degrees'''
    g = g.as_undirected(mode="collapse")
    all_coreness = g.shell_index(mode='ALL')
    # print len(in_coreness), len(out_coreness), len(all_coreness)
    group_labels = ['In-Coreness', 'Out-Coreness', 'UnDir-Coreness']
    pt.plot_config()

    sns.distplot(in_coreness, hist=False, label=group_labels[0])
    sns.distplot(out_coreness, hist=False, label=group_labels[1])
    sns.distplot(all_coreness, hist=False, label=group_labels[2])
    plt.xlim(0, 100)
    plt.xlabel('Coreness')
    plt.ylabel('Density')
    plt.show()


def k_core_g(g):
    g = g.as_undirected(mode="collapse")
    print g.summary()
    index = 1
    stats = []
    print '------------------------------------'
    gc = g.k_core(index)
    while gc.vcount() > 0:
        print index
        print gc.summary()
        node_n = gc.vcount()
        edge_m = gc.ecount()
        density = gc.density()
        avg_path = gc.average_path_length()
        components = gc.clusters()
        comp_count = len(components)
        giant_comp = components.giant()
        giant_comp_r = float(giant_comp.vcount())/node_n
        cluster_co_global = g.transitivity_undirected()
        stat = [node_n, edge_m, density, avg_path, comp_count, giant_comp_r, cluster_co_global
                ]
        stats.append(stat)
        index += 1
        gc = g.k_core(index)
    stats = np.array(stats)
    names = ['#Nodes', '#Edges', 'G-Density', 'Avg-Path', '#Component', 'Giant Component Ratio', 'Transitivity'
             ]
    data = pd.DataFrame(stats, columns=names)
    data.to_csv('data.csv')
    # pt.plot_config()
    # for i in xrange(stats.shape[1]):
    #     plt.clf()
    #     sns.tsplot(data=stats[:,i])
    #     # plt.xlim(0, 100)
    #     plt.xlabel('K-Core')
    #     plt.ylabel(names[i])
    #     plt.show()


if __name__ == '__main__':
    # g = gt.load_network('fed', 'net')
    # pickle.dump(g, open('data/fedfried.pick', 'w'))
    g = pickle.load(open('data/fedfried.pick', 'r'))
    print g.summary()
    # coreness(g)
    k_core_g(g)


