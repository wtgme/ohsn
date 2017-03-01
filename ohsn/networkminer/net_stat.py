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
import ohsn.util.db_util as dbt
import pickle
import operator
import ohsn.util.statis_util as st
import ohsn.util.plot_util as pt
import pymongo


def drop_initials(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i > -1000000000.0]


def display(data, topk=5):
    elist = ['engage.social_contribution',
    'engage.information_productivity',
    'engage.information_attractiveness',
    'engage.information_influence']
    sorted_x = sorted(data.items(), key=operator.itemgetter(1))
    sorted_x.reverse()
    count = 0
    for i in xrange(topk):
        # if 'text_anal' in sorted_x[i][0]:

        '''Exclude social impacts measures'''
        tokens = sorted_x[i][0].split(',')
        if sorted_x[i][0].endswith('*') and tokens[0] not in elist and float(tokens[-2])>0:
        # '''Count all'''
        # if sorted_x[i][0].endswith('*'):
            count += 1
            print sorted_x[i][0]
    print float(count)/(101-4)


def rank_feature(gc, dbname, comname, db_field_names, directed=True):
    g = gt.giant_component(gc, 'WEAK')

    g.vs['nt'] = g.degree(type="in")
    netatt = g.vs['nt']

    # ranks = g.pagerank(weights='weight')
    # g.vs['rank'] = ranks

    # cor = st.tau_coef(g.degree(type="in"), g.vs['rank'])
    # print 'Indegree' + '\t' + str(cor[0]) + '\t' + str(cor[1])
    # cor = st.tau_coef(g.degree(type="out"), g.vs['rank'])
    # print 'Outdegree' + '\t' + str(cor[0]) + '\t' + str(cor[1])

    for db_field_name in db_field_names:
        # print 'Processing ' + db_field_name
        g = gt.add_attribute(g, 'foi', dbname, comname, db_field_name)
        raw_values = np.array(g.vs['foi'])
        values = drop_initials(raw_values)

        if len(values) > 100:
            # maxv, minv = max(values), min(values)
            maxv, minv = np.percentile(values, 97.5), np.percentile(values, 2.5)
            vs = g.vs(foi_ge=minv, foi_le=maxv)
            sg = g.subgraph(vs)

            maxd, mind = np.percentile(netatt, 97.5), np.percentile(netatt, 2.5)
            vs = sg.vs(nt_ge=mind, nt_le=maxd)
            sg = sg.subgraph(vs)

            # cor = st.tau_coef(sg.vs['foi'], sg.vs['nt'])
            # print db_field_name + '\t' + str(len(sg.vs)) + '\t' + str(len(sg.es)) + '\t'\
            #       + str(min(netatt)) + '\t' + str(max(netatt)) + '\t' + str(mind) + '\t'\
            #       +str(maxd) + '\t' \
            #       + str(min(values)) + '\t' + str(max(values)) + '\t' + str(minv) + '\t'\
            #       +str(maxv) + '\t'\
            #       + str(cor[0]) + '\t' + str(cor[1])
            pt.correlation(sg.vs['nt'], sg.vs['foi'], 'Indegree', 'Feature', 'data/'+db_field_name+'.pdf')



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
            vs = g.vs.select(foi_ge=minv, foi_le=maxv)
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
                vs = g.vs.select(foi_ge=minv, foi_le=maxv)
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
            if pval < 0.001:
                output += '***'
                outputs[output] = abs(zscore)
                continue
            if pval < 0.01:
                output += '**'
                outputs[output] = abs(zscore)
                continue
            if pval < 0.05:
                output += '*'
                outputs[output] = abs(zscore)
                continue
            else:
                outputs[output] = abs(zscore)
                continue
    return outputs


def network_stats(dbname, com, fnet, bnet):
    fields = iot.read_fields()
    # print ('Feature, #Nodes, #Edges, %Nodes, %Edges, D_assort, F_assort, F_assort, Mean, STD, z_sore, p_value')
    print ('Network_Feature \t #Nodes \t #Edges \t X_Min \t X_Max \t X_P2.5 \t X_P97.5 \t Y_Min \t Y_Max \t Y_P2.5 \t Y_P97.5 \t Tau_coef \t p_value')
    print 'Following'
    fnetwork = gt.load_network(dbname, fnet)

    '''Out put file for Gephi'''
    # fnetwork.write_dot('friendship.DOT')

    gt.net_stat(fnetwork)
    # outputs = feature_assort_friend(fnetwork, dbname, com, fields, directed=True)
    outputs = rank_feature(fnetwork, dbname, com, fields, directed=True)
    # pickle.dump(outputs, open('data/fnet_assort_all.pick', 'w'))
    # outputs = pickle.load(open('data/fnet_assort_all.pick', 'r'))
    # display(outputs, 101)
    # for beh in ['retweet', 'reply', 'mention']:
    #     print beh
    #     bnetwork = gt.load_beh_network(dbname, bnet, beh)
    #     gt.net_stat(bnetwork)
    #     # outputs = feature_assort_friend(bnetwork, dbname, com, fields, directed=True)
    #     outputs = rank_feature(bnetwork, dbname, com, fields, directed=True)
    #     # pickle.dump(outputs, open('data/'+beh+'_assort_all.pick', 'w'))
    #     # outputs = pickle.load(open('data/'+beh+'_assort_all.pick', 'r'))
    #     # display(outputs, 101)


def calculate_extenal_user():
    # Calculate how many users have been retweeted by ED but do not exist in ED users
    users = set(iot.get_values_one_field('fed', 'com', 'id'))
    print len(users)
    net = dbt.db_connect_col('fed', 'sbnet')
    i, count = 0, 0
    for record in net.find():
        if (record['id0'] not in users) or (record['id1'] not in users):
            i = + 1
        count += 1
    print i, count, float(i)/count




if __name__ == '__main__':
    # network_stats('fed', 'scom', 'snet', 'sbnet')

    # calculate_extenal_user()

    # ED_followee()