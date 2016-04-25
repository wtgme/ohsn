# -*- coding: utf-8 -*-
"""
Created on 14:58, 08/04/16

@author: wt
"""

import ohsn.util.graph_util as gt
from ohsn.util import db_util as dbt
import ohsn.util.plot_util as plot
import pickle
import sys


def core_ed():
    idset = set()
    db = dbt.db_connect_no_auth('fed')
    com = db['com']
    for user in com.find({'level':1}):
        idset.add(user['id_str'])
    return idset


def out_screen_name(idlist):
    db = dbt.db_connect_no_auth('fed')
    com = db['com']
    for ids in idlist:
        print com.find_one({'id': int(ids)})['screen_name']


def plot_pdf(ed, rd, yg, mode='degree'):
    if mode == 'indegree':
        rddseq, ygdseq, eddseq = rd.indegree(), yg.indegree(), ed.indegree()
    elif mode == 'outdegree':
        rddseq, ygdseq, eddseq = rd.outdegree(), yg.outdegree(), ed.outdegree()
    else:
        edu, rdu, ygu = ed.as_undirected(), rd.as_undirected(), yg.as_undirected()
        rddseq, ygdseq, eddseq = rdu.outdegree(), ygu.outdegree(), edu.outdegree()
    plot.plot_pdf_mul_data([rddseq, ygdseq, eddseq], ['--bo', '--r^', '--ks'], mode,  ['Random', 'Young', 'ED'], False)


def friendship_community(dbname, colname, label):
    # fg = gt.load_network(dbname, colname)
    # pickle.dump(fg, open('data/'+label+'-fg.pick', 'w'))
    fg = pickle.load(open('data/'+label+'-fg.pick', 'r'))
    # fgc = gt.giant_component(fg, 'WEAK')
    # gt.summary(fgc)
    # pickle.dump(fgc, open('data/'+label+'-fgc.pick', 'w'))

    # fcoms = gt.community(fg)
    # fclus = fcoms.as_clustering()
    # gt.summary(fclus)
    # pickle.dump(fclus, open('data/'+label+'-fcom.pick', 'w'))
    fclus = pickle.load(open('data/'+label+'-fcom.pick', 'r'))
    layout = fg.layout("fr")
    gt.plot(fg, 'friend_fr.pdf', layout=layout, bbox=(1200, 900))
    gt.plot(fclus, 'friend_comms_fr.pdf', layout=layout, bbox=(1200, 900))


def behavior_community(dbname, colname, label):
    # targed_list = set()
    # db = dbt.db_connect_no_auth('fed')
    # poi = db['com']
    # for user in poi.find({}, ['id']):
    #     targed_list.add(user['id'])

    bg = gt.load_beh_network(dbname, colname)
    gt.summary(bg)
    pickle.dump(bg, open('data/'+label+'-bg.pick', 'w'))
    # bg = pickle.load(open('data/'+label+'-bg.pick', 'r'))

    # bgc = gt.giant_component(bg, 'WEAK')
    # gt.summary(bgc)
    # pickle.dump(bgc, open('data/'+label+'-bgc.pick', 'w'))

    bcoms = gt.community(bg, weighted=True)
    bclus = bcoms.as_clustering()
    gt.summary(bclus)
    pickle.dump(bclus, open('data/'+label+'-bcom.pick', 'w'))

    # bclus = pickle.load(open('data/'+label+'-bcom.pick', 'r'))
    layout = bg.layout("fr")
    gt.plot(bg, 'behaviour_fr.pdf', layout=layout, bbox=(1200, 900))
    gt.plot(bclus, 'behaviour_comms_fr.pdf', layout=layout, bbox=(1200, 900))


if __name__ == '__main__':
    # if sys.argv[1] == 'friend':
    #     friendship_community('fed', 'snet', 'ED')
    # elif sys.argv[1] == 'behavior':
    #     behavior_community('fed', 'snet', 'ED')

    # friendship_community('fed', 'snet', 'ED')
    behavior_community('fed', 'sbnet', 'ED')
    # friendship_community('srd', 'net', 'srd')
    # friendship_community('syg', 'net', 'syg')

    # coreed = core_ed()
    # print 'NO of core ED' +'\t'+ str(len(coreed))

    # print 'Friendship Network'
    # print 'Community Index \t Community Size \t NO of Targeted Core ED \t Ratio of Targeted Core ED'
    # label = 'fed'
    # rdfg = pickle.load(open('data/'+label+'-fg.pick', 'r'))
    # rdf = pickle.load(open('data/'+label+'-fcom.pick', 'r'))
    # index = 0
    # for rdc in rdf:
    #     ids = set()
    #     for v in rdc:
    #         ids.add(rdfg.vs[v]['name'])
    #     print str(index) +'\t'+ str(len(rdc)) +'\t'+ str(len(ids.intersection(coreed))) +'\t'+ str(float(len(ids.intersection(coreed)))/len(coreed))
    #     index += 1

    print '-----------------------'


    # print 'Behavior (retweet, mention, and reply) Network'
    # print 'Community Index \t Community Size \t NO of Targeted Core ED \t Ratio of Targeted Core ED'
    # label = 'fed'
    # ygfg = pickle.load(open('data/'+label+'-bg.pick', 'r'))
    # ygf = pickle.load(open('data/'+label+'-bcom.pick', 'r'))
    # print rdf.membership

    # index = 0
    # for ygc in ygf:
    #     ids = set()
    #     for v in ygc:
    #         ids.add(ygfg.vs[v]['name'])
    #     print str(index) +'\t'+ str(len(ygc)) +'\t'+ str(len(ids.intersection(coreed))) +'\t'+ str(float(len(ids.intersection(coreed)))/len(coreed))
    #     index += 1


    # ed = gt.load_network('fed', 'snet')
    # rd = rdfg.subgraph(rdf[2])
    # print len(ygf[1])
    # yg = ygfg.subgraph(ygf[1])
    # out_screen_name(yg.vs['name'])
    # plot_pdf(ed, rd, yg, 'degree')

    '''Plot ED RD YG'''
    # ed = gt.load_network('sed', 'net')
    # rd = gt.load_network('srd', 'net')
    # # rd = rdfg.subgraph(rdf[1])
    # yg = gt.load_network('syg', 'net')
    # plot_pdf(ed, rd, yg, 'indegree')
    # plot_pdf(ed, rd, yg, 'outdegree')
    # plot_pdf(ed, rd, yg, 'degree')


