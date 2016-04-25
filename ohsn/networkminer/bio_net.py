# -*- coding: utf-8 -*-
"""
Created on 13:50, 25/04/16

@author: wt
Import bio infomration into network, see what distribution of bio information in network

"""

from ohsn.util import db_util as dbt
from ohsn.util import graph_util as grt
from ohsn.util import plot_util as plt

# def load_net(dbname, colname):
#     # TODO
#
# def gw_cw(dbname, colname):
#     # TODO

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
    print poi-users


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
    behaviour('fed', 'sbnet')