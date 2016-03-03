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
    while len(nodes)<n:
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



seed_nodes = io.get_values_one_field('yg', 'ccom', 'id', {'level': 1})
yDG = nt.load_network('yg', 'cnet')
ygc = nt.get_gaint_comp(yDG)
# plot.plot_whole_network(ygc)
for node in seed_nodes:
    if node not in ygc.nodes():
        seed_nodes.remove(node)
print 'Size of seed nodes in gaint components', len(seed_nodes)
# fDG = sample_network(ygc, seed_nodes, 3380)



# eDG = nt.load_network('fed', 'snet')
# ydgs = sorted(nx.degree(yDG).values(),reverse=True)
# edgs = sorted(nx.degree(yDG).values(),reverse=True)
# plot.plot_pdf_mul_data([yDG, eDG], ['--bo', '--r^'], 'Degree',  ['Younger', 'ED'], False)





