# -*- coding: utf-8 -*-
"""
Created on Sat Jun 06 17:52:23 2015

@author: home
"""

from pymongo import Connection
import networkx as nx
import matplotlib.pyplot as plt


DBNAME = 'twitter_test'
COLLECTION = 'testfolloweredges'
COLLECTION = 'testfolloweredgescursored'
COLLECTION = 'testfolloweridsedgescursored'

# connect to the edges database
conn = Connection()
db = conn[DBNAME]
edges = db[COLLECTION]

G=nx.DiGraph()

for edge in edges.find():
    G.add_edge(edge['v0'],edge['v1'])

#export so you can use gephi
#nx.write_graphml(G,'manos-followers-cursored.graphml')
#nx.write_gexf(G, 'manos-followers-cursored.gexf')

#export so you can use gephi
nx.write_graphml(G,'manos-followers-cursored-ids.graphml')
nx.write_gexf(G, 'manos-followers-cursored-ids.gexf')

#nx.draw_spring(G)
#plt.show()