# -*- coding: utf-8 -*-
"""
Created on 17:03, 09/09/16

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.graph_util as gt
import ohsn.util.io_util as iot
import pickle


def generate(dbname, comname, netname, type):
    if type == 'follow':
        g = gt.load_network(dbname, netname)
    else:
        # uids = iot.get_values_one_field(dbname, comname, 'id')
        # pickle.dump(uids, open('data/'+dbname+'-ids.pick', 'w'))
        uids = pickle.load(open('data/'+dbname+'-ids.pick', 'r'))
        g = gt.load_beh_network_subset(uids, dbname, netname, type)

    pickle.dump(g, open('data/'+dbname+type+'.pick', 'w'))

def load(dbname, type):
    return pickle.load(open('data/'+dbname+type+'.pick', 'r'))

if __name__ == '__main__':
    # generate('fed', 'com', 'net', 'follow')
    generate('fed', 'com', 'bnet', 'retweet')
    generate('fed', 'com', 'bnet', 'reply')
    generate('fed', 'com', 'bnet', 'mention')

