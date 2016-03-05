# -*- coding: utf-8 -*-
"""
Created on 1:25 PM, 3/5/16

@author: tw
"""

import sys
sys.path.append('..')
import networkx as nx
import util.net_util as nt
import pickle
import snap

# pickle.dump(fedc, open("data/fedc.p", "wb"))
# randomc = pickle.load(open("data/randomc.p", "rb"))

G = nt.load_network('rd', 'cnet')
nx.write_edgelist(G, "net.edgelist")
Graph = snap.LoadEdgeList(snap.PUNGraph, "net.edgelist", 0, 1, ' ')
CmtyV = snap.TCnComV()
modularity = snap.CommunityGirvanNewman(Graph, CmtyV)
for Cmty in CmtyV:
    print "Community: "
    for NI in Cmty:
        print NI
print "The modularity of the network is %f" % modularity

