# -*- coding: utf-8 -*-
"""
Created on 9:13 PM, 8/11/16

@author: tw
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.graph_util as gt
import pickle


def tag_record(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    print col.count()
    g = gt.load_hashtag_coocurrent_network(dbname, colname)
    pickle.dump(g, open('data/'+'dep_tag.pick', 'w'))
    g = pickle.load(open('data/dep_tag.pick', 'r'))
    gt.net_stat(g)
    g.write_dot('deptag.DOT')

if __name__ == '__main__':
    tag_record('depression', 'search')