# -*- coding: utf-8 -*-
"""
Created on 11:00, 23/09/16

@author: wt
"""

import networkx as nx
from igraph import *
import ohsn.util.graph_util as gt

def statis():
    for i in xrange(1,5):
        path = 'data/Classroom_graphmls/'+'classroom_graph'+str(i)+'.graphml'
        # path ='karate.GraphML'
        # print path
        g = Graph.Read_GraphML(path)
        gt.net_stat(g)

if __name__ == '__main__':
    statis()
