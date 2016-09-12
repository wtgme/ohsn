# -*- coding: utf-8 -*-
"""
Created on 12:16, 08/09/16

@author: wt

Get users that are have many links to the core ED components
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import seaborn as sns
import matplotlib.pyplot as plt
import ohsn.util.graph_util as gt
import ohsn.util.io_util as iot
import pickle
import numpy as np
import pandas as pd
import ohsn.util.network_io as ntt


def ed_user(dbname, colname):
    user_list = []
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    for user in com.find({'level': 1}, ['id']):
        user_list.append(str(user['id']))
    return user_list


def linked(dbname, comname, netname, k):
    # # g = gt.load_network(dbname, netname)
    # # pickle.dump(g, open('data/fed-friend.pick', 'w'))
    # g = pickle.load(open('data/fed-friend.pick', 'r'))
    # g = g.as_undirected(mode="collapse")
    # ed_users = ed_user(dbname, comname)
    # ed_set = set()
    # for ed in ed_users:
    #     try:
    #         v = g.vs.find(name=ed)
    #         ed_set.add(v.index)
    #     except ValueError:
    #         pass
    # print len(ed_set)
    # pickle.dump(ed_set, open('data/ed.pick', 'w'))
    # ed_set = pickle.load(open('data/ed.pick', 'r'))
    #
    # nodes = g.vs.select(name_notin=ed_users)
    #
    # node_ed_neighs = {}
    # for v in nodes:
    #     neighs = g.neighbors(v)
    #     ed_nei = len(ed_set.intersection(set(neighs)))
    #     node_ed_neighs[v['name']] = ed_nei

    # pickle.dump(node_ed_neighs, open('data/node_ed_neighs.pick', 'w'))
    node_ed_neighs = pickle.load(open('data/node_ed_neighs.pick', 'r'))

    ks = np.array([node_ed_neighs[key] for key in node_ed_neighs.keys()])
    # max_x = np.percentile(ks, 97.5)
    # min_x = np.percentile(ks, 2.5)
    # print min_x, max_x
    # lsl = np.where(np.logical_and(ks>=min_x, ks<=max_x))
    # print ks[lsl]

    df = pd.DataFrame({'NO.ED-Friends': ks})
    df.hist(bins=(max(ks)-min(ks)+1))
    # sns.distplot(ks, bins=(max(ks)-min(ks)+1))
    plt.xscale('log')
    plt.yscale('log')
    plt.show()
    return node_ed_neighs


# def triangles():
#     g = pickle.load(open('data/fed-friend.pick', 'r'))
#     g = g.as_undirected(mode="collapse")
#     ed_set = pickle.load(open('data/ed.pick', 'r'))
#     cliques = g.cliques(min=3, max=3)
#     pickle.dump(cliques, open('data/cliques.pick', 'w'))
#     cliques = pickle.load(open('data/cliques.pick', 'r'))
#     results = set()
#     for i, j, k in cliques:
#         nodes = set([g.vs[i].index, g.vs[j].index, g.vs[k].index])
#         inter = ed_set.intersection(nodes)
#         if inter == 2:
#             newnode = nodes-ed_set
#             print g.vs[newnode]['name']
#             results.add(newnode)
#     print len(results)


def triangles(dbname, type):
    '''Load networks'''
    g = ntt.loadnet(dbname, type)
    g = g.as_undirected(mode="collapse")
    print g.vcount()
    print g.ecount()

    '''Map User ID to Node ID in Graph'''
    ed_users = ed_user(dbname, 'com')
    ed_set = set()
    for ed in ed_users:
        try:
            v = g.vs.find(name=ed)
            ed_set.add(v.index)
        except ValueError:
            pass
    print len(ed_set)

    '''Find triangles such that two nodes are core ed and the rest is new users '''
    result = set()
    ed_list = list(ed_set)
    for i in xrange(len(ed_list)):
        ui = ed_list[i]
        nui = set(g.neighbors(ui))
        for j in xrange(i, len(ed_list)):
            uj = ed_list[j]
            if uj in nui:
                nuj = set(g.neighbors(uj))
                for v in nui.intersection(nuj):
                    result.add(v)

    ids = [int(g.vs[v]['name']) for v in result]
    pickle.dump(ids, open('data/'+dbname+type+'triangle.pick', 'w'))

    '''Verify triangle users'''
    db = dbt.db_connect_no_auth('fed')
    com = db['com']
    for v in ids:
        user = com.find_one({'id': int(v)})
        print user['screen_name'].encode('utf-8'), ' '.join(user['description'].split()).encode('utf-8')


if __name__ == '__main__':
    # linked('fed', 'com', 'net', 1)
    # triangles('fed', 'follow')
    # triangles('fed', 'retweet')
    # triangles('fed', 'reply')
    triangles('fed', 'mention')


