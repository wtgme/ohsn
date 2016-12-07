# -*- coding: utf-8 -*-
"""
Created on 14:58, 08/04/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
reload(sys)
sys.setdefaultencoding('utf8')
from ohsn.util import graph_util as gt
from ohsn.util import db_util as dbt
import ohsn.util.io_util as iot
from ohsn.util import plot_util as plot
# from ohsn.textprocessor import topic_model
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import ohsn.util.network_io as ntt
import random as rand


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


def community_topic(g, clus, dbname, colname, timename):
    for clu in clus:
        print '----------------------------------'
        uset = set()
        for v in clu:
            # print int(g.vs[v]['name'])
            uset.add(int(g.vs[v]['name']))
        # topic_model.topic_model(dbname, colname, timename, uset)


def communtiy_feature(dbname, typename):
    fg = ntt.loadnet(dbname, typename)

    fcoms = gt.fast_community(fg)
    pickle.dump(fcoms, open('data/'+dbname+typename+'com.pick', 'w'))
    fcoms = pickle.load(open('data/'+dbname+typename+'com.pick', 'r'))
    fclus = fcoms.as_clustering()
    gt.summary(fclus)

    """Compare difference of features in cummunities"""
    features = [
        'liwc_anal.result.i',
        'liwc_anal.result.we',
        'liwc_anal.result.bio',
        'liwc_anal.result.body',
        'liwc_anal.result.health',
        'liwc_anal.result.posemo',
        'liwc_anal.result.negemo',
        'liwc_anal.result.ingest',
        'liwc_anal.result.anx',
        'liwc_anal.result.anger',
        'liwc_anal.result.sad'
                ]
    therh = 0.1 * fg.vcount()
    for feature in features:
        data = []
        for clu in fclus:
            if len(clu) > therh:
                ulist = set()
                for v in clu:
                    ulist.add(int(fg.vs[v]['name']))
                ulist = list(ulist)
                clu_values = iot.get_values_one_field(dbname, 'com', feature, {'id': {'$in': ulist}})
                data.append(clu_values)

        plot.plot_config()
        for i in xrange(len(data)):
            sns.distplot(data[i], hist=False, label=str(i)+':'+str(len(data[i])))
        plt.xlabel(feature)
        plt.ylabel('PDF')
        # plt.show()
        plt.savefig(feature+typename+'_com.pdf')
        plt.clf()


def friendship_community(dbname, colname, label):
    # fg = gt.load_network(dbname, colname)
    # gt.summary(fg)
    # pickle.dump(fg, open('data/'+label+'-fg.pick', 'w'))
    fg = pickle.load(open('data/'+label+'-fg.pick', 'r'))

    # fgc = gt.giant_component(fg, 'WEAK')
    # gt.summary(fgc)
    # pickle.dump(fgc, open('data/'+label+'-fgc.pick', 'w'))

    # fcoms = gt.fast_community(fg)
    # pickle.dump(fcoms, open('data/'+label+'-fcom.pick', 'w'))
    fcoms = pickle.load(open('data/'+label+'-fcom.pick', 'r'))
    # gt.plot(fcoms, 'friend_comms_den.pdf', bbox=(1200, 900))
    fclus = fcoms.as_clustering()
    gt.summary(fclus)
    print fclus.recalculate_modularity()
    community_topic(fg, fclus, dbname, 'scom', 'stimeline')

    # # fclus = pickle.load(open('data/'+label+'-fcom.pick', 'r'))
    # layout = fg.layout("fr")
    # # gt.plot(fg, 'friend_fr.pdf', layout=layout, bbox=(1200, 900))
    # gt.plot(fclus, 'friend_comms_fr.pdf', layout=layout, mark_groups=True, bbox=(1200, 900))
    # gt.comm_plot(fg, fclus, 'friend_comms_fr.pdf', fclus.membership)


def friendship_community_vis(dbname, colname, filename, ctype):
    '''Out graph for vis.js visualization'''
    ed_users = iot.get_values_one_field(dbname, 'scom', 'id')
    dbcom = dbt.db_connect_col(dbname, 'com')
    fg = gt.load_network(dbname, colname)
    # fg = gt.load_beh_network(dbname, colname, 'retweet')
    # gt.net_stat(fg)
    # fg = fg.as_undirected(mode="mutual")
    # gt.net_stat(fg)

    fg = gt.giant_component(fg, 'WEAK')
    gt.net_stat(fg)

    if ctype == 'ml':
        com = fg.community_multilevel(weights='weight', return_levels=False)
    elif ctype == 'lp':
        fgu = fg.as_undirected(combine_edges=sum)
        com = fgu.community_leading_eigenvector(clusters=2, weights='weight')
        # print init.membership
        # com = fg.community_label_propagation(weights='weight', initial=init.membership)
        print com.membership
    else:
        com = fg.community_infomap(edge_weights='weight')
    fg.vs['group'] = com.membership

    # edges = fg.es.select(weight_gt=3)
    # print 'Filtered edges: %d' %len(edges)
    # fg = fg.subgraph_edges(edges)
    # gt.net_stat(fg)

    # fg.vs['degree'] = fg.degree(mode="all")
    # nodes = fg.vs.select(degree_gt=10)
    # fg = fg.subgraph(nodes)
    # gt.net_stat(fg)

    Coo={}
    for x in fg.vs['group']:
        Coo[x]=(rand.randint(-1000, 1000), rand.randint(-1000, 1000))

    with open('data/' + ctype + '_' +filename+'_fnet.js', 'w') as fw:
        fw.write('var nodes = [\n')
        for idv, v in enumerate(fg.vs):
            user = dbcom.find_one({'id': int(fg.vs[idv]['name'])})
            desc = ' '.join(user['description'].replace('\'', '').replace('\"', '').split())
            fw.write('{id: ' + str(idv+1) + ', '+
                     'label: \'' + user['screen_name'] +'\', ' +
                     'value: ' + str(fg.degree(idv, mode="all")) + ', ' +
                     'title: \'UID: ' + str(fg.vs[idv]['name']) +
                     '<br> Screen Name: ' + user['screen_name'] +
                     '<br> Followers: ' + str(user['followers_count']) +
                     '<br> Followees: ' + str(user['friends_count']) +
                     '<br> Tweets: ' + str(user['statuses_count']) +
                     '<br> Description: ' + str(desc.encode('utf-8')) +
                     '<br> Group: ' + str(fg.vs[idv]['group']) + '\', ' +
                     'x: ' + str(Coo[fg.vs[idv]['group']][0]+rand.randint(0, 300)) + ', ' +
                     'y: ' + str(Coo[fg.vs[idv]['group']][1]+rand.randint(0, 300)) + ', ' +
                     'group: ' + str(fg.vs[idv]['group']))
            if int(fg.vs[idv]['name']) in ed_users:
                fw.write('shape: ' + '\'triangle\'')
            else:
                fw.write('shape: ' + '\'circle\'')
            fw.write('}, \n')
        fw.write('];\n var edges = [\n')
        for ide, e in enumerate(fg.es):
            fw.write('{from: ' + str(e.source+1) + ', ' +
                     'to: ' + str(e.target+1) + ', ' +
                     'arrows: ' + '\'to\'' + ', ' +
                     'title: \' Tags: ' + fg.vs[e.source]['name'] + ' ' + fg.vs[e.target]['name'] +
                     '<br> Co-occurrence: ' + str(fg.es[ide]['weight']) + '\', ' +
                     'value: ' + str(fg.es[ide]['weight']) +
                     '},\n') #str(fg.es[ide]['weight'])
        fw.write('];\n')

def behavior_community(dbname, colname, label):
    # targed_list = set()
    # db = dbt.db_connect_no_auth('fed')
    # poi = db['com']
    # for user in poi.find({}, ['id']):
    #     targed_list.add(user['id'])

    # bg = gt.load_beh_network(dbname, colname)
    # gt.summary(bg)
    # pickle.dump(bg, open('data/'+label+'-bg.pick', 'w'))
    bg = pickle.load(open('data/'+label+'-bg.pick', 'r'))

    # bgc = gt.giant_component(bg, 'WEAK')
    # gt.summary(bgc)
    # pickle.dump(bgc, open('data/'+label+'-bgc.pick', 'w'))

    # bcoms = gt.fast_community(bg)
    # pickle.dump(bcoms, open('data/'+label+'-bcom.pick', 'w'))
    bcoms = pickle.load(open('data/'+label+'-bcom.pick', 'r'))
    # gt.plot(bcoms, 'commu_comms_den.pdf', bbox=(1200, 900))
    bclus = bcoms.as_clustering()
    gt.summary(bclus)
    print bclus.recalculate_modularity()
    community_topic(bg, bclus, dbname, 'scom', 'stimeline')


    # # gt.comm_plot(bg, fclus, fclus.membership)
    # # bclus = pickle.load(open('data/'+label+'-bcom.pick', 'r'))
    # layout = bg.layout("fr")
    # # # gt.plot(bg, 'behaviour_fr.pdf', layout=layout, weighted=False, bbox=(1200, 900))
    # gt.plot(bclus, label+'_comms_fr.pdf', layout=layout, mark_groups=True, bbox=(1200, 900))
    # gt.comm_plot(bg, bclus, label+'_comms_fr.pdf', bclus.membership)


if __name__ == '__main__':
    # if sys.argv[1] == 'friend':
    #     friendship_community('fed', 'snet', 'ED')
    # elif sys.argv[1] == 'behavior':
    #     behavior_community('fed', 'snet', 'ED')

    # friendship_community('fed', 'snet', 'ED')
    # behavior_community('fed', 'sbnet', 'communi')
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

    # '''Plot ED RD YG'''
    # ed = gt.load_network('ded', 'net')
    # rd = gt.load_network('drd', 'net')
    # yg = gt.load_network('dyg', 'net')
    # plot_pdf(ed, rd, yg, 'indegree')
    # plot_pdf(ed, rd, yg, 'outdegree')
    # plot_pdf(ed, rd, yg, 'degree')


    """Plot distributions of communities in terms of LIWC features"""
    # communtiy_feature('fed', 'follow')
    # communtiy_feature('fed', 'retweet')
    # communtiy_feature('fed', 'reply')
    # communtiy_feature('fed', 'mention')


    '''Out graph for vis.js visualization'''

    # friendship_community_vis('fed', 'snet', 'ed', 'ml')
    friendship_community_vis('fed', 'net', 'fed', 'lp')


