# -*- coding: utf-8 -*-
"""
Created on 14:58, 08/04/16

@author: wt
"""
import sys
sys.path.append('..')
import util.graph_util as gt
import util.db_util as dbt
import util.plot_util as plot
import pickle


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
    fg = gt.load_network(dbname, colname)
    pickle.dump(fg, open('data/'+label+'-fg.pick', 'w'))
    fgc = gt.giant_component(fg, 'WEAK')
    gt.summary(fgc)
    pickle.dump(fgc, open('data/'+label+'-fgc.pick', 'w'))
    fcoms = gt.community(fgc)
    fclus = fcoms.as_clustering()
    gt.summary(fclus)
    pickle.dump(fclus, open('data/'+label+'-fcom.pick', 'w'))


def behavior_community():
    targed_list = set()
    db = dbt.db_connect_no_auth('fed')
    poi = db['com']
    for user in poi.find({}, ['id']):
        targed_list.add(user['id'])

    bg = gt.load_beh_network('fed', 'bnet', targed_list)
    pickle.dump(bg, open('data/ed-bg.pick', 'w'))
    bgc = gt.giant_component(bg, 'WEAK')
    gt.summary(bgc)
    pickle.dump(bgc, open('data/ed-bgc.pick', 'w'))
    bcoms = gt.community(bgc)
    bclus = bcoms.as_clustering()
    gt.summary(bclus)
    pickle.dump(bclus, open('data/ed-bcom.pick', 'w'))


if __name__ == '__main__':
    # if sys.argv[1] == 'friend':
    #     friendship_community()
    # elif sys.argv[1] == 'behavior':
    #     behavior_community()

    # friendship_community('srd', 'net', 'srd')
    # friendship_community('syg', 'net', 'syg')

    coreed = core_ed()
    print 'NO of core ED' +'\t'+ str(len(coreed))

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


    print 'Behavior (retweet, mention, and reply) Network'
    print 'Community Index \t Community Size \t NO of Targeted Core ED \t Ratio of Targeted Core ED'
    label = 'fed'
    ygfg = pickle.load(open('data/'+label+'-bg.pick', 'r'))
    ygf = pickle.load(open('data/'+label+'-bcom.pick', 'r'))
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
    print len(ygf[1])
    yg = ygfg.subgraph(ygf[1])
    out_screen_name(yg.vs['name'])
    # plot_pdf(ed, rd, yg, 'degree')

    '''Plot ED RD YG'''
    # ed = gt.load_network('sed', 'net')
    # rd = gt.load_network('srd', 'net')
    # # rd = rdfg.subgraph(rdf[1])
    # yg = gt.load_network('syg', 'net')
    # plot_pdf(ed, rd, yg, 'indegree')
    # plot_pdf(ed, rd, yg, 'outdegree')
    # plot_pdf(ed, rd, yg, 'degree')


