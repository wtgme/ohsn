# -*- coding: utf-8 -*-
"""
Created on 15:55, 29/04/16

@author: wt
Calculate the propotions of ED-friends and NON-ED-friends
"""

import ohsn.util.db_util as dbt
import ohsn.util.graph_util as gt
import pickle

def target_set(dbname, comname):
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    uset = set()
    for user in com.find({}, ['id']):
        uset.add(user['id'])
    return uset


def friend_dis(dbname, comname, netname, tagets):
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    g = gt.load_network(dbname, netname)
    gt.summary(g)
    for user in com.find({}, ['id', 'net_anal']):
        uid = user['id']
        values = user.get('net_anal', {'mined': True})
        node_exist = True
        try:
           g.vs.find(name=str(uid))
        except ValueError:
            node_exist = False
        if node_exist:
            # followers = g.neighborhood(str(uid), mode='out')
            # followings = g.neighborhood(str(uid), mode='in')
            followers = g.successors(str(uid))
            followings = g.predecessors(str(uid))
            # print followers
            # print followings
            follower_set = set(int(name) for name in g.vs[followers]['name'])
            following_set = set(int(name) for name in g.vs[followings]['name'])
            friend_set = follower_set | following_set
            # print follower_set
            # print following_set
            follower = len(follower_set)
            if follower == 0:
                follower = 1
            following = len(following_set)
            if following == 0:
                following = 1
            friend = len(friend_set)
            if friend == 0:
                friend = 1
            ed_follower = len(tagets & follower_set)
            ed_following = len(tagets & following_set)
            ed_friend = len(tagets & friend_set)

            ed_follower_p = float(ed_follower)/follower
            ed_following_p = float(ed_following)/following
            ed_friend_p = float(ed_friend)/friend
            net_sta = {}
            net_sta['follower_no'] = follower
            net_sta['following_no'] = following
            net_sta['friend_no'] = friend
            net_sta['ed_follower_no'] = ed_follower
            net_sta['ed_following_no'] = ed_following
            net_sta['ed_friend_no'] = ed_friend
            net_sta['ed_follower_p'] = ed_follower_p
            net_sta['ed_following_p'] = ed_following_p
            net_sta['ed_friend_p'] = ed_friend_p
            net_sta['non_ed_follower_p'] = 1 - ed_follower_p
            net_sta['non_ed_following_p'] = 1 - ed_following_p
            net_sta['non_ed_friend_p'] = 1 - ed_friend_p
            values['ed_proportion'] = net_sta
            com.update_one({'id': uid}, {'$set': {'net_anal': values}}, upsert=True)


def test_igraph(uid):
    db = dbt.db_connect_no_auth('fed')
    net = db['net']
    # uid = 1071274447
    uset = set()
    for r in net.find({'user': uid}, ['follower']):
        uset.add(r['follower'])
    print uset
    print len(uset)
    # g = gt.load_network('fed', 'net')
    # pickle.dump(g, open('data/g.pick', 'w'))
    g = pickle.load(open('data/g.pick', 'r'))
    followers = g.successors(str(uid))
    followings = g.predecessors(str(uid))
    followersn = g.neighborhood(str(uid), mode='out')
    followingsn = g.neighborhood(str(uid), mode='in')
    print g.vs[followers]['name']
    print g.vs[followersn]['name']
    print len(g.vs[followers]['name'])
    print len(g.vs[followersn]['name'])
    print g.vs[followings]['name']
    print g.vs[followingsn]['name']
    print len(g.vs[followings]['name'])
    print len(g.vs[followingsn]['name'])

if __name__ == '__main__':
    target = target_set('fed', 'scom')
    friend_dis('fed', 'scom', 'net', target)
    # test_igraph(2881955738)

