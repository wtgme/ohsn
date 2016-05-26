# -*- coding: utf-8 -*-
"""
Created on 16:53, 26/05/16

@author: wt
Analysis whether a user often retweet one person
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.graph_util as gt
import ohsn.util.db_util as dbt
import pickle
import ohsn.util.io_util as iot


def bahavior_net(dbname, comname, bnetname, btype):
    userlist = iot.get_values_one_field(dbname, comname, 'id',
                                        {'timeline_count': {'$gt': 0}})
    return gt.load_all_beh_network(userlist, dbname, bnetname, btype)

if __name__ == '__main__':
    dbnames = ['fed', 'random', 'young']
    behaviors = ['retweet', 'reply', 'mention', 'communication', 'all']
    for dbname in dbnames:
        for behavior in behaviors:
            g = bahavior_net(dbname, 'scom', 'bnet', behavior)
            pickle.dump(g, open('data/'+dbname+'_'+behavior+'.pick', 'w'))

