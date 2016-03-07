# -*- coding: utf-8 -*-
"""
Created on 1:25 PM, 3/5/16

@author: tw
"""

import sys
sys.path.append('..')
import util.net_util as nt
import util.plot_util as plot
import pickle
import snap

# pickle.dump(fedc, open("data/fedc.p", "wb"))
# randomc = pickle.load(open("data/randomc.p", "rb"))


def snap_comm():
    G = nt.load_network('rd', 'cnet')
    nx.write_edgelist(G, "data/net.data")
    Graph = snap.LoadEdgeList(snap.PUNGraph, "data/net.data", 0, 1, ' ')
    CmtyV = snap.TCnComV()
    modularity = snap.CommunityGirvanNewman(Graph, CmtyV)
    for Cmty in CmtyV:
        print "Community: "
        for NI in Cmty:
            print NI
    print "The modularity of the network is %f" % modularity


def nx_comm_plot(dbname, colname):
    G = nt.load_network(dbname, colname)
    plot.network_top(G, dbname+'.png')
    comp = nt.girvan_newman(G)
    pickle.dump(comp, open('data/'+dbname+'.p', "wb"))


nx_comm_plot('rd', 'cnet')
nx_comm_plot('yg', 'cnet')


