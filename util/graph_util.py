# -*- coding: utf-8 -*-
"""
Created on 20:05, 07/04/16

@author: wt
"""

from igraph import *
import db_util as dbt
import util.plot_util as plot
import net_util as nt
from time import time


def load_network(db_name, collection='None'):
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, []
    for row in cols.find({}):
        n2 = str(row['user'])
        n1 = str(row['follower'])
        n1id = name_map.get(n1, len(name_map))
        name_map[n1] = n1id
        n2id = name_map.get(n2, len(name_map))
        name_map[n2] = n2id
        # Slower than above
        # n1id = name_map.get(n1, -1)
        # if n1id == -1:
        #     n1id = len(name_map)
        #     name_map[n1] = n1id
        #
        # n2id = name_map.get(n2, -1)
        # if n2id == -1:
        #     n2id = len(name_map)
        #     name_map[n2] = n2id
        edges.append((n1id, n2id))
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(edges)
    return g


def load_beh_network(db_name, collection='None'):
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, {}
    for row in cols.find({}):
    # for row in cols.find({'type': {'$in': [1, 2, 3]}}, no_cursor_timeout=True):
        n1 = str(row['id0'])
        n2 = str(row['id1'])
        n1id = name_map.get(n1, len(name_map))
        name_map[n1] = n1id
        n2id = name_map.get(n2, len(name_map))
        name_map[n2] = n2id
        wt = edges.get((n1id, n2id), 0)
        edges[(n1id, n2id)] = wt + 1
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(edges.keys())
    g.es["weight"] = edges.values()
    return g

t0 = time()
g = load_network('fed', 'snet')
indegree1 = g.indegree()
outdegree1 = g.outdegree()
# plot.pdf_plot_one_data(indegree, 'indegree', min(indegree), max(indegree))
t1 = time()
DG = nt.load_network('fed', 'snet')
indegree2 = DG.in_degree().values()
outdegree2 = DG.out_degree().values()
# plot.pdf_plot_one_data(indegree, 'indegree', min(indegree), max(indegree))
t2 = time()
print list(set(indegree1) - set(indegree2))
print list(set(outdegree1) - set(outdegree2))
print 'function vers1 takes %f' %(t1-t0)
print 'function vers2 takes %f' %(t2-t1)

for v in DG.nodes():
    ist1 = DG.in_degree(v)
    ist2 = g.indegree(str(v))
    if ist1 != ist2:
        print 'Fa'
print 'finished'


g = load_beh_network('fed', 'sbnet')
indegree1 = g.indegree()
outdegree1 = g.outdegree()
inst1 = g.strength(mode='IN')
outst1 = g.strength(mode='OUT')

DG = nt.load_behavior_network('fed', 'sbnet')
indegree2 = DG.in_degree().values()
outdegree2 = DG.out_degree().values()
inst2 = DG.in_degree(weight='weight').values()
outst2 = DG.out_degree(weight='weight').values()

print list(set(indegree1) - set(indegree2))
print list(set(outdegree1) - set(outdegree2))
print list(set(inst1) - set(inst2))
print list(set(outst1) - set(outst2))

for v in DG.nodes():
    ist1 = DG.in_degree(v, weight='weight')
    ist2 = g.strength(str(v), mode='IN', weights='weight')
    if ist1 != ist2:
        print ist1, ist2
        # print 'Fa'
