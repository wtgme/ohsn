# -*- coding: utf-8 -*-
"""
Created on 20:05, 07/04/16

@author: wt
"""

from igraph import *
import db_util as dbt
import plot_util as splot
import pickle


def load_network(db_name, collection='None'):
    ''' Friendship network: directed network'''
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, set()
    for row in cols.find({}):
        n1 = str(row['user'])
        n2 = str(row['follower'])
        n1id = name_map.get(n1, len(name_map))
        name_map[n1] = n1id
        n2id = name_map.get(n2, len(name_map))
        name_map[n2] = n2id
        edges.add((n1id, n2id))
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(list(edges))
    return g


    '''Tweet: 0
    Retweet: 1;
    Reply: 2;
    Direct Mention: 3;
    undirect mention: 4 '''
def load_beh_network(db_name, collection='None'):
    ''' behavior network: directed weighted network'''
    if collection is 'None':
        cols = db_name
    else:
        db = dbt.db_connect_no_auth(db_name)
        cols = db[collection]
    name_map, edges = {}, {}
    # for row in cols.find({}):
    for row in cols.find({'type': {'$in': [2]}}, no_cursor_timeout=True):
        n1 = str(row['id0'])
        n2 = str(row['id1'])
        if n1 != n2:
            n1id = name_map.get(n1, len(name_map))
            name_map[n1] = n1id
            n2id = name_map.get(n2, len(name_map))
            name_map[n2] = n2id
            wt = edges.get((n1id, n2id), 0)
            edges[(n1id, n2id)] = wt + 1
    g = Graph(len(name_map), directed=True)
    g.vs["name"] = list(sorted(name_map, key=name_map.get))
    g.add_edges(edges.keys())
    # g.es["weight"] = edges.values()
    return g


def add_attribute(g, name, dbname, colname, field):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    g.vs[name] = 0.0
    for x in com.find({field: {'$exists': True}}, ['id', field]):
        uid = x['id']
        exist = True
        try:
            v = g.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            if '.' in field:
                levels = field.split('.')
                t = x.get(levels[0])
                for level in levels[1:]:
                    t = t.get(level)
                    if t is None:
                        break
                v[name] = t
            else:
                v[name] = x.get(field)
    return g


def giant_component(g, mode):
    com = g.clusters(mode=mode)
    print 'The processed network has components:', len(com)
    return com.giant()


def community(g, weighted=False):
    '''Only for Undirected graph'''
    if g.is_directed():
        if weighted:
            g = g.as_undirected(combine_edges='sum')
        else:
            g = g.as_undirected()
    if weighted:
        return g.community_fastgreedy(weights='weight')
    else:
        return g.community_fastgreedy()


if __name__ == '__main__':
    # g = load_network('fed', 'snet')
    # pickle.dump(g, open('data/fg.pick', 'w'))
    # # g = pickle.load(open('data/bg.pick', 'r'))
    # g = add_attribute(g, 'gbmi', 'fed', 'scom', 'text_anal.gbmi.value')
    # for v in g.vs:
    #     print v['name'], v['gbmi']

    g = Graph([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)])
    g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
    g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
    g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
    g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]
    g.es['weight'] = 2.0
    layout = g.layout("kk")
    plot(g, layout=layout, bbox=(1200, 900))


    # print g.es[g.get_eid('480706562', '386203927')]
    # print g.es[g.get_eid('1092937046', '777200318')]
    # print g.es[g.get_eid('1129480146', '919267472')]
    # print g.es[g.get_eid('431013874', '518335800')]
    # print g.es[g.get_eid('249683957', '548884928')]
    # indegree = g.indegree()
    # outdegree = g.outdegree()
    # instrength = g.strength(mode='IN', weights='weight')
    # outstrenght = g.strength(mode='OUT', weights='weight')
    # print min(indegree), max(indegree)
    # splot.pdf_plot_one_data(indegree, 'Indegree')
    # splot.pdf_plot_one_data(outdegree, 'Outdegree')



    # g = load_network('fed', 'snet')
    # gc = giant_component(g, 'WEAK')
    # summary(gc)
    # coms = community(gc)
    # clus = coms.as_clustering()
    # summary(clus)
    # for clu in clus:
    #     summary(clu)
    #
    # DG = nt.load_network('fed', 'snet')
    # gc2 = nt.get_gaint_comp(DG)
    # print gc2.number_of_nodes(), gc2.number_of_edges()
    #
    # t0 = time()
    # g = load_network('fed', 'snet')
    # indegree1 = g.indegree()
    # outdegree1 = g.outdegree()
    # # plot.pdf_plot_one_data(indegree, 'indegree', min(indegree), max(indegree))
    # t1 = time()
    # DG = nt.load_network('fed', 'snet')
    # indegree2 = DG.in_degree().values()
    # outdegree2 = DG.out_degree().values()
    # # plot.pdf_plot_one_data(indegree, 'indegree', min(indegree), max(indegree))
    # t2 = time()
    # print list(set(indegree1) - set(indegree2))
    # print list(set(outdegree1) - set(outdegree2))
    # print 'function vers1 takes %f' %(t1-t0)
    # print 'function vers2 takes %f' %(t2-t1)
    #
    # for v in DG.nodes():
    #     ist1 = DG.in_degree(v)
    #     ist2 = g.indegree(str(v))
    #     if ist1 != ist2:
    #         print 'Fa'
    # print 'finished'
    #
    #
    # g = load_beh_network('fed', 'sbnet')
    # indegree1 = g.indegree()
    # outdegree1 = g.outdegree()
    # inst1 = g.strength(mode='IN')
    # outst1 = g.strength(mode='OUT')
    #
    # DG = nt.load_behavior_network('fed', 'sbnet')
    # indegree2 = DG.in_degree().values()
    # outdegree2 = DG.out_degree().values()
    # inst2 = DG.in_degree(weight='weight').values()
    # outst2 = DG.out_degree(weight='weight').values()
    #
    # print list(set(indegree1) - set(indegree2))
    # print list(set(outdegree1) - set(outdegree2))
    # print list(set(inst1) - set(inst2))
    # print list(set(outst1) - set(outst2))
    #
    # for v in DG.nodes():
    #     ist1 = DG.in_degree(v, weight='weight')
    #     ist2 = g.strength(str(v), mode='IN', weights='weight')
    #     if ist1 != ist2:
    #         print ist1, ist2
    #         # print 'Fa'
