# -*- coding: utf-8 -*-
"""
Created on 13:50, 25/04/16

@author: wt
Import bio infomration into network, see what distribution of bio information in network

"""

from ohsn.util import db_util as dbt
from ohsn.util import graph_util as grt
from ohsn.util import plot_util as splt
import numpy as np


def drop_zeros(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i>0]


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def fnet_bmi(dbname, colname, comname, typename, name, field):
    # g = grt.load_network(dbname, colname)
    g = grt.load_beh_network(dbname, colname)
    g = grt.add_attribute(g, name, dbname, comname, field)
    values = np.array(g.vs[name])
    bins = np.array([0.0, 1.0, 15.0, 16, 18.5, 25, 30, 35])
    color_map = {1: '#FFFFFF00', 2: '#ffffb2FF', 3: '#fed976FF',
                 4: '#feb24cFF', 5: '#fd8d3cFF', 6: '#fc4e2aFF',
                 7: '#e31a1cFF', 8: '#b10026FF', 9: '#00441bFF'}
    inds = np.digitize(values, bins)
    print min(values), max(values), min(inds), max(inds)
    # splt.pdf_plot_one_data(values, 'GBMI', linear_bins=True)
    layout = g.layout("fr")
    grt.plot(g, typename+'_'+name+'.pdf', layout=layout, bbox=(1200, 900),
             vertex_color=[grt.color_name_to_rgba(color_map[i]) for i in inds])


def frienship(dbname, colname, comname):
    db = dbt.db_connect_no_auth(dbname)
    net = db[colname]
    com = db[comname]
    poi = set()
    for user in com.find():
        poi.add(user['id'])
    users = set()
    for rel in net.find():
        user = rel['user']
        follow = rel['follower']
        users.add(user)
        users.add(follow)

    print len(users)
    print len(poi-users)
    print poi-users
    allnet = db['net']
    for user in poi-users:
        friends = set()
        for u in allnet.find({'user': user}):
            friends.add(u['follower'])
        for u in allnet.find({'follower': user}):
            friends.add(u['user'])
        print user, len(friends), poi.intersection(friends)



def behaviour(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    sbnet = db[colname]
    users = set()
    for rel in sbnet.find({'type': {'$in': [2, 3]}}):
        users.add(rel['id0'])
        users.add(rel['id1'])
    print len(users)


if __name__ == '__main__':
    # frienship('fed', 'snet', 'scom')
    fnet_bmi('fed', 'sbnet', 'scom', 'behaviour', 'gbmi', 'text_anal.gbmi.value')
    # behaviour('fed', 'sbnet')