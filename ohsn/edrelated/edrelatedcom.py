# -*- coding: utf-8 -*-
"""
Created on 15:48, 09/08/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
from ohsn.api import profiles_check
import ohsn.util.graph_util as gt
import pickle


def rec_user(dbname, colname):
    user_lit = []
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    count = 0
    i = 0
    for user in com.find({}, ['id', 'description']):
        if 'recover' in (user['description'].strip().lower().replace("-", "").replace('_', '')):
            # print user['id'], ' '.join(user['description'].split()).encode('utf-8')
            user_lit.append(user['id'])
            count += 1
        i += 1
    print count
    return user_lit


def ed_user(dbname, colname):
    user_lit = []
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    count = 0
    i = 0
    for user in com.find({}, ['id', 'description']):
        if profiles_check.check_ed_related_profile(user['description']):
            # print user['id'], ' '.join(user['description'].split()).encode('utf-8')
            user_lit.append(user['id'])
            count += 1
        i += 1
    print count
    return user_lit


def plot_graph(g):
    layout = g.layout("fr")
    color_dict = {0: "blue", 1: "red"}
    visual_style = {}
    visual_style["vertex_size"] = 5
    visual_style["vertex_color"] = [color_dict[flag] for flag in g.vs["rec"]]
    # visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
    visual_style["margin"] = 20
    visual_style["bbox"] = (1024, 768)
    visual_style["edge_arrow_size"] = 0.2
    visual_style["edge_arrow_width"] = 0.2
    visual_style["layout"] = layout
    gt.plot(g, **visual_style)

def network(dbname, colname, netname):
    # # ed_usersd = ed_user(dbname, colname)
    # # pickle.dump(ed_usersd, open('data/ed_users.pick', 'w'))
    # ed_usersd = pickle.load(open('data/ed_users.pick', 'r'))
    #
    # # rec_usersd = rec_user(dbname, colname)
    # # pickle.dump(rec_usersd, open('data/rec_users.pick', 'w'))
    # rec_usersd = pickle.load(open('data/rec_users.pick', 'r'))
    #
    #
    # inlist = list(set(ed_usersd).union(set(rec_usersd)))
    #
    # print len(inlist)
    # g = gt.load_network_subset(inlist, dbname, netname)
    # g.vs['rec'] = 0
    # for uid in rec_usersd:
    #     exist = True
    #     try:
    #         v = g.vs.find(name=str(uid))
    #     except ValueError:
    #         exist = False
    #     if exist:
    #         v['rec'] = 1
    # pickle.dump(g, open('data/rec_friendship.pick', 'w'))
    rg = pickle.load(open('data/rec_friendship.pick', 'r'))
    # g.write_gml('data/rec_friendship.GML')
    # g.write_dot('data/rec_friendship.DOT')

    gc = gt.giant_component(rg, 'WEAK')
    comm = gt.fast_community(gc, False)
    fclus = comm.as_clustering(2)
    communit_topinflu(fclus, None)
    # gt.comm_plot(gc, fclus, 'rec_friend_fr.pdf', fclus.membership)

    # plot_graph(g)


def benetwork(dbname, type, netname):
    # ed_usersd = pickle.load(open('data/ed_users.pick', 'r'))
    # rec_usersd = pickle.load(open('data/rec_users.pick', 'r'))
    # inlist = list(set(ed_usersd).union(set(rec_usersd)))
    # g = gt.load_beh_network_subset(inlist, dbname, netname, type)
    # g.vs['rec'] = 0
    # for uid in rec_usersd:
    #     exist = True
    #     try:
    #         v = g.vs.find(name=str(uid))
    #     except ValueError:
    #         exist = False
    #     if exist:
    #         v['rec'] = 1
    # pickle.dump(g, open('data/rec_'+type+'.pick', 'w'))
    rg = pickle.load(open('data/rec_'+type+'.pick', 'r'))
    # plot_graph(g)

    gc = gt.giant_component(rg, 'WEAK')
    comm = gt.fast_community(gc, True)
    fclus = comm.as_clustering(2)
    communit_topinflu(fclus, 'weight')
    # gt.comm_plot(gc, fclus, 'rec_'+type+'_fr.pdf', fclus.membership)


def communit_topinflu(fclus, weight):
    for g in fclus.subgraphs():
        n = g.vcount()
        rec_n = len(g.vs.select(rec_eq=1))
        ed_n = len(g.vs.select(rec_eq=0))
        print n, float(rec_n) / n, float(ed_n) / n
        db = dbt.db_connect_no_auth('fed')
        com = db['com']
        for uid in gt.most_pagerank(g, 15, weight):
            user = com.find_one({'id': int(uid)}, ['id', 'screen_name', 'name', 'description'])
            print str(user['id']) + '\t' + user['screen_name'].encode('utf-8') + '\t' + user['name'].encode('utf-8') +'\t'+ ' '.join(user['description'].split()).encode('utf-8')


if __name__ == '__main__':
    # ed_users = ed_user('fed', 'com')
    # rec_users = rec_user('fed', 'com')
    # print len(set(ed_users).intersection(rec_users))
    print 'Friendship'
    network('fed', 'com', 'net')
    types = ['retweet', 'reply', 'mention', 'communication', 'all']
    for type in types:
        print type
        benetwork('fed', type, 'bnet')


