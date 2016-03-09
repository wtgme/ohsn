# -*- coding: utf-8 -*-
"""
Created on 1:25 PM, 3/5/16

@author: tw
"""

import sys
sys.path.append('..')
import util.net_util as nt
import util.plot_util as plot
import util.db_util as dbt
import pickle
import snap
import networkx as nx

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


def purn_net(dbname):
    db = dbt.db_connect_no_auth(dbname)
    poi = db['ccom']
    net = db['cnet']
    snet = db['scnet']

    target = set()
    for poi in poi.find({'level': {'$lt': 3}}, ['id']):
        target.add(poi['id'])
    print 'Targeted Users:', len(target)

    for rec in net.find():
        if rec['user'] in target and rec['follower'] in target:
            snet.insert(rec)


def nx_comm_plot(dbname, colname):
    G = nt.load_network(dbname, colname)
    GC = nt.get_gaint_comp(G)
    nt.net_statis(GC)
    plot.network_top(GC)
    comp = nt.girvan_newman(GC)
    pickle.dump(comp, open('data/'+dbname+'.pick', "wb"))

# purn_net('rd')
nx_comm_plot('rd', 'scnet')
# nx_comm_plot('yg', 'cnet')


