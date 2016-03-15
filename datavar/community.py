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
    for poi in poi.find({'level': {'$lt': 4}}, ['id']):
        target.add(poi['id'])
    print 'Targeted Users:', len(target)

    for rec in net.find():
        if rec['user'] in target and rec['follower'] in target:
            snet.insert(rec)


def out_net(G, name):
    fw = open('data/'+name+'.pairs', 'w')
    id_map = {}
    id_map_inv = {}
    edgs = {}
    for e in G.edges_iter():
        n1, n2 = e
        if n1 == n2:
            print 'self following', n1, n2
        n1id = id_map.get(n1, len(id_map)+1)
        id_map[n1] = n1id
        id_map_inv[n1id] = n1
        n2id = id_map.get(n2, len(id_map)+1)
        id_map[n2] = n2id
        id_map_inv[n2id] = n2
        if n1id == n2id:
            print 'self following ids', n1id, n2id
        flist = edgs.get(n1id, [])
        flist.append(n2id)
        edgs[n1id] = flist

    for key in sorted(edgs):
        for key2 in sorted(edgs[key]):
            fw.write(str(key) + '\t' + str(key2) + '\n')
    fw.close()
    pickle.dump(id_map_inv, open('data/'+name+'-id.pick', 'w'))


def out_net_commudet(dbname, colname, name):
    # transform the largest component to undirect for community detection
    G = nt.load_network(dbname, colname)
    GC = nt.get_gaint_comp(G)
    # nt.net_statis(GC)
    GCG = GC.to_undirected()
    # nt.net_statis(GCG)
    print GCG.number_of_selfloops()

    out_net(GCG, name)
    # nx.write_edgelist(GCG, "data/net.data", delimiter='\t', data=False)
    # plot.network_top(GC)
    # comp = nt.girvan_newman(GC)
    # pickle.dump(comp, open('data/'+dbname+'.pick', "wb"))


def plot_communty(dbname, colname, name, commline):
    G = nt.load_network(dbname, colname)
    GC = nt.get_gaint_comp(G)

    id_map = pickle.load(open('data/'+name+'-id.pick', 'r'))
    nodelist = list()

    fr = open('data/'+name+'-fc_best.groups', 'r')
    line = ''
    while commline not in line:
        line = fr.readline()
    print line
    print '----------------------------'
    for line in fr.readlines():
        if 'GROUP' in line:
            break
        else:
            nodelist.append(id_map[int(line.strip())])
    print 'node size:', str(len(nodelist))
    # plot.network_top(GC.subgraph(nodelist))
    return GC.subgraph(nodelist)




# purn_net('yg')
# out_net_commudet('yg', 'tnet', 'ygtime')

# rdcom = plot_communty('rd', 'scnet', 'rd2l', 'GROUP[ 74 ][ 2691 ]')
rdcom = plot_communty('rd', 'tnet', 'rdtime', 'GROUP[ 1539 ][ 4641 ]')
# ygcom = plot_communty('yg', 'scnet', 'yg3l', 'GROUP[ 33 ][ 3883 ]')
ygcom = plot_communty('yg', 'tnet', 'ygtime', 'GROUP[ 2360 ][ 1966 ]')
fed = nt.load_network('fed', 'snet')
nt.net_statis(rdcom)
nt.net_statis(ygcom)
nt.net_statis(fed)
rddseq = sorted(nx.degree(rdcom).values(),reverse=True)
ygdseq = sorted(nx.degree(ygcom).values(), reverse=True)
eddseq = sorted(nx.degree(fed).values(), reverse=True)
plot.plot_pdf_mul_data([rddseq, ygdseq, eddseq], ['--bo', '--r^', '--ks'], 'Degree',  ['Random', 'Young', 'ED'], False)


