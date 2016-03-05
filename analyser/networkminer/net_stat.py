# -*- coding: utf-8 -*-
"""
Created on 16:49, 02/03/16

@author: wt
"""
import sys
sys.path.append('..')
from networkx import *
import util.net_util as nt
import util.io_util as io
from random import choice
import util.plot_util as plot


def random_walk(DG, n):
    G = DG.to_undirected()
    start_node = choice(G.nodes())
    nodes = set()
    while len(nodes) < n:
        nodes.add(start_node)
        start_node = choice(G.neighbors(start_node))
    return nodes


def sample_network(DG, seed_nodes, size):
    seed_set = seed_nodes
    smp_set = list(set(DG.nodes()) - set(seed_set))
    startDG = DG.subgraph(seed_set)
    while nt.size_gaint_comp(startDG)[0] < size:
        print '-----------add node------------------'
        sample = choice(smp_set)
        seed_nodes.append(sample)
        smp_set.remove(sample)
        startDG = DG.subgraph(seed_set)
    return startDG


def gc_stat(dbname, colname):
    DG = nt.load_network(dbname, colname)
    # nt.net_statis(DG)
    GC = nt.get_gaint_comp(DG)
    UGC = GC.to_undirected()
    # nt.net_statis(UGC)
    return UGC

print '----------------------'
yg = gc_stat('yg', 'snet')

print '----------------------'
rd = gc_stat('rd', 'snet')

print '----------------------'
ed = gc_stat('fed', 'snet')


# eDG = nt.load_network('fed', 'snet')
ydgs = sorted(nx.degree(yg).values(),reverse=True)
rdgs = sorted(nx.degree(rd).values(),reverse=True)
edgs = sorted(nx.degree(ed).values(),reverse=True)

plot.plot_pdf_mul_data([ydgs, rdgs, edgs], ['--bo', '--r^', '--ks'], 'Degree',  labels=['YG', 'RD', 'ED'], linear_bins=False)





