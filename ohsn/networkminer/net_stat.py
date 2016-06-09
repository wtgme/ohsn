# -*- coding: utf-8 -*-
"""
Created on 16:49, 02/03/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.graph_util as gt


def network_stats(dbname, fnet, bnet):
    fnetwork = gt.load_network(dbname, fnet)
    gt.net_stat(fnetwork)
    for beh in ['retweet', 'reply', 'mention']:
        bnetwork = gt.load_beh_network(dbname, bnet, beh)
        print beh
        gt.net_stat(bnetwork)


if __name__ == '__main__':
    network_stats('fed', 'snet', 'sbnet')