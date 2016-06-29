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
import pickle
import operator


def drop_initials(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i > -1000000000.0]


def display(data, topk=5):
    sorted_x = sorted(data.items(), key=operator.itemgetter(1))
    sorted_x.reverse()
    for i in xrange(topk):
        if 'text_anal' in sorted_x[i][0]:
            print sorted_x[i][0]

def feature_assort_friend(g, dbname, comname, db_field_names, directed=True):
    '''Using iGraph
    Assigning values different from zero or one to the adjacency matrix will be translated to one,
    unless the graph is weighted, in which case the numbers will be treated as weights
    '''
    node_size, edge_size = g.vcount(), g.ecount()
    outputs = {}
    print ('Feature, #Nodes, #Edges, %Nodes, %Edges, D_assort, F_assort, F_assort, Mean, STD, z_sore, p_value')
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
                      + str(float(t_node_size)/node_size) + ',' + str(float(t_edge_size)/edge_size)+ ',' \
                      + str(sg.assortativity_degree(directed=directed)) + ',' \
                      + str(sg.assortativity('foi', 'foi', directed=directed)) + ','
            raw_assort = sg.assortativity('foi', 'foi', directed=directed)
            ass_list = list()
            for i in xrange(3000):
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
            zscore = (raw_assort-amean)/astd
            # print pval
            output += str(raw_assort) + ',' + str(amean) + ',' + str(astd) + ',' + str(zscore) + ',' + str(pval)
            print output
            if pval <= 0.001:
                output += '***'
                outputs[output] = abs(zscore)
                continue
            if pval <= 0.01:
                output += '**'
                outputs[output] = abs(zscore)
                continue
            if pval <= 0.05:
                output += '*'
                outputs[output] = abs(zscore)
                continue
            else:
                outputs[output] = abs(zscore)
                continue
    return outputs


def network_stats(dbname, com, fnet, bnet):
    fields = iot.read_fields()
    print ('Feature, #Nodes, #Edges, %Nodes, %Edges, D_assort, F_assort, F_assort, Mean, STD, z_sore, p_value')
    print 'Following'
    fnetwork = gt.load_network(dbname, fnet)
    gt.net_stat(fnetwork)
    # outputs = feature_assort_friend(fnetwork, dbname, com, fields, directed=True)
    # pickle.dump(outputs, open('data/fnet_assort_all.pick', 'w'))
    # outputs = pickle.load(open('data/fnet_assort_all.pick', 'r'))
    # display(outputs, 100)
    for beh in ['retweet', 'reply', 'mention']:
        print beh
        bnetwork = gt.load_beh_network(dbname, bnet, beh)
        gt.net_stat(bnetwork)
        # outputs = feature_assort_friend(bnetwork, dbname, com, fields, directed=True)
        # pickle.dump(outputs, open('data/'+beh+'_assort_all.pick', 'w'))
        # outputs = pickle.load(open('data/'+beh+'_assort_all.pick', 'r'))
        # display(outputs, 100)


if __name__ == '__main__':
    network_stats('fed', 'scom', 'snet', 'sbnet')