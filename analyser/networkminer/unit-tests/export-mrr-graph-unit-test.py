# -*- coding: utf-8 -*-
"""
Created on Sat Jun 06 17:52:23 2015

@author: home
"""

import networkx as nx
import matplotlib.pyplot as plt

import pymongo
import datetime

MONGOURL = 'localhost'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'
MRR_COL = 'mrredges'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    
    poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL

    mrredges = db[MRR_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + MRR_COL

    #mrredges = db[WeightedEdges_COL]
    #print  MONGOUSER +" connected to " + DBNAME  + "." + WeightedEdges_COL
    # create an index! 

except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()

G=nx.DiGraph()

print 'mentioned\t' + str(mrredges.find({'relationship':'mentioned'}).count())
print 'reply-to\t' + str(mrredges.find({'relationship':'reply-to'}).count())
print "retweets\t" + str(mrredges.find({'relationship':'retweet'}).count())

for edge in edges.find({'relationship':'mentioned'}):
    G.add_edge(edge['v0'],edge['v1'], relationship='mentioned')

for edge in edges.find({'relationship':'reply-to'}):
    G.add_edge(edge['v0'],edge['v1'], relationship='reply-to')

for edge in edges.find({'relationship':'retweet'}):
    G.add_edge(edge['v0'],edge['v1'], relationship='retweet')




#export so you can use gephi
#nx.write_graphml(G,'manos-followers-cursored.graphml')
#nx.write_gexf(G, 'manos-followers-cursored.gexf')

#export so you can use gephi
nx.write_graphml(G,'manos-followers-cursored-ids.graphml')
nx.write_gexf(G, 'manos-followers-cursored-ids.gexf')

#nx.draw_spring(G)
#plt.show()
