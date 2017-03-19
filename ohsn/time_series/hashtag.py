# -*- coding: utf-8 -*-
"""
Created on 18:59, 19/03/17

@author: wt

Get recovery related hashtags
"""



import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.graph_util as gt
import ohsn.util.io_util as iot
import numpy as np


def ed_users_hashtags():
    # construct hashtag network used by core ed users
    # users = iot.get_values_one_field('fed', 'scom', 'id')
    # g = gt.load_hashtag_coocurrent_network_undir('fed', 'prorec_tag', users)
    # g.write_graphml('ed_hashtag.graphml')
    g = gt.Graph.Read_GraphML('ed_hashtag.graphml')
    gt.summary(g)

    recovery = g.vs.find(name="recovery")
    recovery_index = recovery.index

    # sims = g.similarity_inverse_log_weighted()
    # for v in g.vs:
    #     print v['name'], sims[recovery_index][v.index]


    vw_sum = sum(g.vs["weight"])
    for edge in g.es:
        source_vertex_id = edge.source
        target_vertex_id = edge.target
        source_vertex = g.vs[source_vertex_id]
        target_vertex = g.vs[target_vertex_id]
        ew = edge['weight']
        edge['pmi'] = np.log(float(ew*vw_sum)/(source_vertex['weight']*target_vertex['weight']))
    print len(g.es.select(_source=recovery_index))
    for edge in g.es.select(_source=recovery_index):
        print g.vs[edge.target]['name'], edge['pmi']

if __name__ == '__main__':
    ed_users_hashtags()
