# -*- coding: utf-8 -*-
"""
Created on 14:58, 08/04/16

@author: wt
"""
import sys
sys.path.append('..')
import util.graph_util as gt
import util.db_util as dbt
import pickle


def friendship_community():
    fg = gt.load_network('fed', 'net')
    pickle.dump(fg, open('ed-fg.pick', 'w'))
    fgc = gt.giant_component(fg, 'WEAK')
    gt.summary(fgc)
    pickle.dump(fgc, open('ed-fgc.pick', 'w'))
    fcoms = gt.community(fgc)
    fclus = fcoms.as_clustering()
    gt.summary(fclus)
    pickle.dump(fclus, open('ed-fcom.pick', 'w'))


def behavior_community():
    targed_list = []
    db = dbt.db_connect_no_auth('fed')
    poi = db['com']
    for user in poi.find({}, ['id_str']):
        targed_list.append(user['id_str'])

    bg = gt.load_beh_network('fed', 'bnet')
    bg = bg.subgraph(targed_list)
    pickle.dump(bg, open('ed-bg.pick', 'w'))
    bgc = gt.giant_component(bg, 'WEAK')
    gt.summary(bgc)
    pickle.dump(bgc, open('ed-bgc.pick', 'w'))
    bcoms = gt.community(bgc)
    bclus = bcoms.as_clustering()
    gt.summary(bclus)
    pickle.dump(bclus, open('ed-bcom.pick', 'w'))


if __name__ == '__main__':
    if sys.argv[1] == 'friend':
        friendship_community()
    elif sys.argv[1] == 'behavior':
        behavior_community()
