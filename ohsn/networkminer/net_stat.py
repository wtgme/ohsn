# -*- coding: utf-8 -*-
"""
Created on 16:49, 02/03/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.graph_util as gt
import ohsn.util.io_util as iot
import numpy as np
import operator


def drop_initials(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i > -1000000000.0]


def display(data, topk=3):
    sorted_x = sorted(data.items(), key=operator.itemgetter(1))
    for i in xrange(topk):
        print sorted_x[i][0]

def feature_assort_friend(g, dbname, comname, db_field_names, directed=True):
    '''Using iGraph
    Assigning values different from zero or one to the adjacency matrix will be translated to one,
    unless the graph is weighted, in which case the numbers will be treated as weights
    '''
    node_size, edge_size = g.vcount(), g.ecount()
    outputs = {}
    outputs.append('Feature, #Node, #Edge, P_node, P_edge, D_assort, F_assort, Mean, STD, p_value')
    for db_field_name in db_field_names:
        # print 'Processing ' + db_field_name
        g = gt.add_attribute(g, 'foi', dbname, comname, db_field_name)
        raw_values = np.array(g.vs['foi'])
        values = drop_initials(raw_values)

        if len(values) > 100:
            output = ''
            # maxv, minv = np.percentile(values, 97.5), np.percentile(values, 2.5)
            maxv, minv = max(values), min(values)
            vs = g.vs(foi_ge=minv, foi_le=maxv)
            sg = g.subgraph(vs)
            t_node_size, t_edge_size = len(sg.vs), len(sg.es)
            output += db_field_name + ',' + str(t_node_size) + ',' + str(t_edge_size) + ',' \
                      + str(round(float(t_node_size)/node_size, 3)) + ',' + str(round(float(t_edge_size)/edge_size, 3))+ ',' \
                      + str(round(sg.assortativity_degree(directed=directed), 3)) + ',' \
                      + str(round(sg.assortativity('foi',
                                                   'foi', directed=directed), 3)) + ','
            raw_assort = sg.assortativity('foi', 'foi', directed=directed)
            ass_list = list()
            for i in xrange(2000):
                np.random.shuffle(raw_values)
                g.vs["foi"] = raw_values
                vs = g.vs(foi_ge=minv, foi_le=maxv)
                sg = g.subgraph(vs)
                ass_list.append(sg.assortativity('foi', 'foi', directed=directed))
            ass_list = np.array(ass_list)
            amean, astd = np.mean(ass_list), np.std(ass_list)

            absobserved = abs(raw_assort)
            pval = (np.sum(ass_list >= absobserved) +
                    np.sum(ass_list <= -absobserved))/float(len(ass_list))
            print pval
            output += str(round(amean, 3)) + ',' + str(round(astd, 3)) + ',' + str(round(pval, 3))
            if pval <= 0.0001:
                output += '***'
                outputs[output] = pval
                continue
            if pval <= 0.001:
                output += '**'
                outputs[output] = pval
                continue
            if pval <= 0.01:
                output += '*'
                outputs[output] = pval
                continue
            else:
                outputs[output] = pval
                continue
    display(outputs)
    return outputs


def network_stats(dbname, com, fnet, bnet):
    fields = iot.read_fields()
    fnetwork = gt.load_network(dbname, fnet)
    gt.net_stat(fnetwork)
    feature_assort_friend(fnetwork, dbname, com, fields, directed=True)
    for beh in ['retweet', 'reply', 'mention']:
        bnetwork = gt.load_beh_network(dbname, bnet, beh)
        print beh
        gt.net_stat(bnetwork)
        feature_assort_friend(bnetwork, dbname, com, fields, directed=True)


if __name__ == '__main__':
    network_stats('fed', 'snet', 'sbnet')