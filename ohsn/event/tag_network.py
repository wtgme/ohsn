# -*- coding: utf-8 -*-
"""
Created on 9:13 PM, 8/11/16

@author: tw
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import matplotlib
import ohsn.util.graph_util as gt
import ohsn.util.io_util as iot
import pickle
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import ohsn.util.plot_util as pll
import igraph as ig

def pdf(data):
    pll.plot_pdf_mul_data([data], ['Edge Weight'], ['r'], ['o'], labels=['Edge Weight'],
                          linear_bins=False, central=False, fit=True, fitranges=[(1, 10000)])

def tag_record(dbname, colname, filename):
    # ed_users = iot.get_values_one_field(dbname, 'scom', 'id')
    # print len(ed_users)
    # g = gt.load_hashtag_coocurrent_network(dbname, colname, ed_users)
    # pickle.dump(g, open('data/'+filename+'_tag.pick', 'w'))
    g = pickle.load(open('data/'+filename+'_tag.pick', 'r'))
    gt.net_stat(g)
    nodes = g.vs.select(weight_gt=3)
    print 'Filtered nodes: %d' %len(nodes)
    g = g.subgraph(nodes)
    # nodes = g.vs.select(user_gt=3)
    # print 'Filtered nodes: %d' %len(nodes)
    # g = g.subgraph(nodes)
    # gt.net_stat(g)
    # edges = g.es.select(weight_gt=3)
    # print 'Filtered edges: %d' %len(edges)
    # g = g.subgraph_edges(edges)
    # edges = g.es.select(weight_gt=1)
    # print len(edges)
    gt.net_stat(g)
    plot_graph(g, 'ed-hashtag')
    g.write_graphml(filename+'_tag.graphml')
    return g


def plot_graph(g, filename):
    visual_style = {}
    layout = g.layout("fr")
    visual_style["vertex_size"] = np.log2(g.vs['weight'])*2
    visual_style["vertex_color"] = 'tomato'
    visual_style["vertex_label"] = ''
    # visual_style["edge_width"] = np.array(g.es['weight'])*10
    visual_style["edge_width"] = np.array(g.es['weight'])+1
    # visual_style["edge_color"] = 'slategrey'
    visual_style["layout"] = layout
    visual_style["margin"] = 10
    visual_style["bbox"] = (1024, 768)
    ig.plot(g, filename+'.pdf', **visual_style)


def pmi(g, filename):
    print g.is_loop()
    vw_sum = sum(g.vs["weight"])
    for edge in g.es:
        source_vertex_id = edge.source
        target_vertex_id = edge.target
        source_vertex = g.vs[source_vertex_id]
        target_vertex = g.vs[target_vertex_id]
        ew = edge['weight']
        edge['pmi'] = np.log(float(ew*vw_sum)/(source_vertex['weight']*target_vertex['weight']))
    # pickle.dump(g, open('data/'+filename+'_pmi_tag.pick', 'w'))
    # g = pickle.load(open('data/'+filename+'_pmi_tag.pick', 'r'))
    # pdf(g.es['weight'])
    # plot_graph(g, 'ed-hashtag')
    g.write_graphml(filename+'_pmi_tag.graphml')


# def plot_graph(filename):
#     g = gta.load_graph(filename)
#     age = g.vertex_properties["weight"]
#
#     pos = gta.sfdp_layout(g)
#     gta.graph_draw(g, pos, output_size=(1000, 1000), vertex_color=[1,1,1,0],
#                vertex_fill_color=age, vertex_size=1, edge_pen_width=1.2,
#                vcmap=matplotlib.cm.gist_heat_r, output="hashtag.pdf")

if __name__ == '__main__':
    g = tag_record('fed', 'timeline', 'ed')
    # pmi(g, filename='ed')

    # plot_graph('ed_tag.graphml')
