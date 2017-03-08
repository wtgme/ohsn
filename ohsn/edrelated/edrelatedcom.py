# -*- coding: utf-8 -*-
"""
Created on 15:48, 09/08/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
from ohsn.api import profiles_check
import ohsn.util.io_util as iot
import ohsn.util.graph_util as gt
import pickle
import re
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import ohsn.util.plot_util as pltt


def print_user_profile(dbname, colname):
    """print profiles of users"""
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    for user in com.find({}, ['id', 'id_str', 'screen_name', 'description']):
        print user['id_str'], user['screen_name'], ' '.join(user['description'].split()).encode('utf-8')


def rec_user(dbname, colname):
    """Get recovery users"""
    user_lit = []
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    count = 0
    for user in com.find({}, ['id', 'id_str', 'screen_name', 'description']):
        if profiles_check.check_ed_related_profile(user['description']):
            text = user['description'].strip().lower().replace("-", "").replace('_', '')
            sentences = re.split( r"\s*[;:`\"()?!{}]\s*|--+|\s*-\s+|''|\.\s|\.$|\.\.+|¡°|¡±", text )
            FLAG = False
            for sentence in sentences:
                if 'recover' in sentence:
                    if 'not' not in sentence and 'don\'t' not in sentence \
                            and 'anti' not in sentence and 'non' not in sentence\
                            and 'relapse' not in sentence:
                        FLAG = True
                # if 'struggl' in sentence:
                #     if 'thin' not in sentence and 'weight' not in sentence \
                #             and 'mirror' not in sentence and 'figure' not in sentence \
                #             and 'food' not in sentence and 'body' not in sentence\
                #             and 'proed' not in sentence and 'proana' not in sentence and 'promia' not in sentence:
                #         FLAG = True
                # if 'fight' in sentence:
                #     if 'thin' not in sentence and 'weight' not in sentence \
                #             and 'mirror' not in sentence and 'figure' not in sentence \
                #             and 'food' not in sentence and 'body' not in sentence:
                #         FLAG = True
            # for sentence in sentences:
            #     if 'proed' in sentence or 'proana' in sentence or 'promia' in sentence:
            #         if 'not' not in sentence and \
            #                         'don\'t' not in sentence and \
            #                         'anti' not in sentence:
            #             FLAG = False
            if FLAG:
                print user['id_str'], user['screen_name'], ' '.join(user['description'].split()).encode('utf-8')
                user_lit.append(str(user['id']))
                count += 1
    print count
    return user_lit


def proed_users(dbname, colname):
    '''Get pro-ED users'''
    user_list = []
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    count = 0
    for user in com.find({}, ['id', 'id_str', 'screen_name', 'description']):
        if profiles_check.check_ed_related_profile(user['description']):
            text = user['description'].strip().lower().replace("-", "").replace('_', '')
            sentences = re.split( r"\s*[;:`\"()?!{}]\s*|--+|\s*-\s+|''|\.\s|\.$|\.\.+|¡°|¡±", text )
            FLAG = False
            for sentence in sentences:
                if 'proed' in sentence or 'proana' in sentence \
                        or 'prothin' in sentence or 'thinspo' in sentence \
                        or 'bonespo' in sentence or 'thinspiration' in sentence\
                        or 'proanamia' in sentence or 'promia' in sentence:
                    if 'not' not in sentence and 'don\'t' not in sentence and 'anti' not in sentence and 'non' not in sentence:
                        FLAG = True
            if FLAG:
                print user['id_str'], user['screen_name'], ' '.join(user['description'].split()).encode('utf-8')
                user_list.append(str(user['id']))
                count += 1
    print count
    return user_list


def ed_user(dbname, colname):
    '''Get ED users'''
    user_lit = []
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    count = 0
    i = 0
    for user in com.find({}, ['id', 'description']):
        if profiles_check.check_ed_related_profile(user['description']):
            print user['id'], ' '.join(user['description'].split()).encode('utf-8')
            user_lit.append(user['id'])
            count += 1
        i += 1
    print count
    return user_lit


def plot_graph(g):
    '''Plot graph of network'''
    layout = g.layout("fr")
    color_dict = {0: "blue", 1: "red"}
    visual_style = {}
    visual_style["vertex_size"] = 5
    visual_style["vertex_color"] = [color_dict[flag] for flag in g.vs["rec"]]
    # visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
    visual_style["margin"] = 20
    visual_style["bbox"] = (1024, 768)
    visual_style["edge_arrow_size"] = 0.2
    visual_style["edge_arrow_width"] = 0.2
    visual_style["layout"] = layout
    gt.plot(g, **visual_style)

def network(dbname, colname, netname):
    '''Get users' friendship network'''
    # # ed_usersd = ed_user(dbname, colname)
    # # pickle.dump(ed_usersd, open('data/ed_users.pick', 'w'))
    # ed_usersd = pickle.load(open('data/ed_users.pick', 'r'))
    #
    # # rec_usersd = rec_user(dbname, colname)
    # # pickle.dump(rec_usersd, open('data/rec_users.pick', 'w'))
    # rec_usersd = pickle.load(open('data/rec_users.pick', 'r'))
    #
    #
    # inlist = list(set(ed_usersd).union(set(rec_usersd)))
    #
    # print len(inlist)
    # g = gt.load_network_subset(inlist, dbname, netname)
    # g.vs['rec'] = 0
    # for uid in rec_usersd:
    #     exist = True
    #     try:
    #         v = g.vs.find(name=str(uid))
    #     except ValueError:
    #         exist = False
    #     if exist:
    #         v['rec'] = 1
    # pickle.dump(g, open('data/rec_friendship.pick', 'w'))
    rg = pickle.load(open('data/rec_friendship.pick', 'r'))
    # g.write_gml('data/rec_friendship.GML')
    # g.write_dot('data/rec_friendship.DOT')

    gc = gt.giant_component(rg, 'WEAK')
    comm = gt.fast_community(gc, False)
    fclus = comm.as_clustering(2)
    communit_topinflu(fclus, None)
    # gt.comm_plot(gc, fclus, 'rec_friend_fr.pdf', fclus.membership)

    # plot_graph(g)


def benetwork(dbname, type, netname):
    '''Get users' behavior networks'''
    # ed_usersd = pickle.load(open('data/ed_users.pick', 'r'))
    # rec_usersd = pickle.load(open('data/rec_users.pick', 'r'))
    # inlist = list(set(ed_usersd).union(set(rec_usersd)))
    # g = gt.load_beh_network_subset(inlist, dbname, netname, type)
    # g.vs['rec'] = 0
    # for uid in rec_usersd:
    #     exist = True
    #     try:
    #         v = g.vs.find(name=str(uid))
    #     except ValueError:
    #         exist = False
    #     if exist:
    #         v['rec'] = 1
    # pickle.dump(g, open('data/rec_'+type+'.pick', 'w'))
    rg = pickle.load(open('data/rec_'+type+'.pick', 'r'))
    # plot_graph(g)

    gc = gt.giant_component(rg, 'WEAK')
    comm = gt.fast_community(gc, True)
    fclus = comm.as_clustering(2)
    communit_topinflu(fclus, 'weight')
    # gt.comm_plot(gc, fclus, 'rec_'+type+'_fr.pdf', fclus.membership)


def communit_topinflu(fclus, weight):
    for g in fclus.subgraphs():
        n = g.vcount()
        rec_n = len(g.vs.select(rec_eq=1))
        ed_n = len(g.vs.select(rec_eq=0))
        print n, float(rec_n) / n, float(ed_n) / n
        db = dbt.db_connect_no_auth('fed')
        com = db['com']
        for uid in gt.most_pagerank(g, 15, weight):
            user = com.find_one({'id': int(uid)}, ['id', 'screen_name', 'name', 'description'])
            print str(user['id']) + '\t' + user['screen_name'].encode('utf-8') + '\t' + user['name'].encode('utf-8') +'\t'+ ' '.join(user['description'].split()).encode('utf-8')


def pro_ed_rec_network(dbname, comname, netname):
    g = gt.load_network(dbname, netname)
    # g = gt.load_beh_network(dbname, 'sbnet', 'mention')
    rec_users = rec_user(dbname, comname)
    pro_users = proed_users(dbname, comname)

    print len(rec_users)
    print len(pro_users)
    g.vs['set'] = 0
    for user in rec_users:
        exist = True
        try:
            v = g.vs.find(name=str(user))
        except ValueError:
            exist = False
        if exist:
            v['set'] += 1 # +1 Pro-rec
    for user in pro_users:
        exist = True
        try:
            v = g.vs.find(name=str(user))
        except ValueError:
            exist = False
        if exist:
            v['set'] -= 1 # -1 Pro-ED
    vs = g.vs(set_ne=0)
    sg = g.subgraph(vs)
    gt.net_stat(sg)
    # sgc = gt.giant_component(sg)
    # gt.net_stat(sgc)

    '''Test signifi'''
    raw_assort = sg.assortativity('set', 'set', directed=True)
    raw_values = np.array(sg.vs['set'])
    ass_list = list()
    for i in xrange(3000):
        np.random.shuffle(raw_values)
        sg.vs["set"] = raw_values
        ass_list.append(sg.assortativity('set', 'set', directed=True))
    ass_list = np.array(ass_list)
    amean, astd = np.mean(ass_list), np.std(ass_list)

    absobserved = abs(raw_assort)
    pval = (np.sum(ass_list >= absobserved) +
            np.sum(ass_list <= -absobserved))/float(len(ass_list))
    zscore = (raw_assort-amean)/astd
    print '%.3f, %.3f, %.3f, %.3f, %.3f' %(raw_assort, amean, astd, zscore, pval)
    # print str(raw_assort) + ',' + str(amean) + ',' + str(astd) + ',' + str(zscore) + ',' + str(pval)
    sg.write_graphml('pro-ed-rec-mention.graphml')

def distribution_change(dbname, colname):
    rec_users1 = pickle.load(open('data/pro-recovery.pick', 'r'))
    pro_ed = pickle.load(open('data/pro_ed.pick', 'r'))
    print len(rec_users1)
    print len(pro_ed)
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
    names = ['I', 'We', 'Bio', 'Body', 'Health', 'Posemo', 'Negemo', 'Ingest', 'Anx', 'Anger', 'Sad']
    df = pd.DataFrame()
    pltt.plot_config()
    for i in xrange(len(features)):
        feature = features[i]
        old_values = iot.get_values_one_field(dbname, colname, feature, {'id':{'$in': rec_users1}})
        df1 = pd.DataFrame({'Feature': names[i], 'Group': 'Pro-Recovery', 'Values': old_values})
        new_values = iot.get_values_one_field(dbname, colname, feature, {'id':{'$in': pro_ed}})
        df2 = pd.DataFrame({'Feature': names[i], 'Group': 'Pro-ED', 'Values': new_values})
        df1 = df1.append(df2)
        if len(df) == 0:
            df = df1
        else:
            df = df.append(df1)
        '''Plot Individual'''
        # sns.distplot(old_values, hist=False, label='Before')
        # sns.distplot(new_values, hist=False, label='After')
        d, p = stats.ks_2samp(old_values, new_values)
        print (names[i] + ', %.3f(%.3f), %.3f(%.3f), %.3f(%.3f)' %((np.mean(old_values)), (np.std(old_values)),
                                                 (np.mean(new_values)), (np.std(new_values)), d, p))
        # plt.xlabel(feature)
        # plt.ylabel('PDF')
        # # plt.show()
        # plt.savefig(dbname+'_'+feature+'_time.pdf')
        # plt.clf()
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    # sns.violinplot(x="Feature", y="Values", hue="Time", data=df, split=True,
    #                inner="quart", palette={"Before": "b", "After": "y"})
    # sns.despine(left=True)
    sns.boxplot(x="Feature", y="Values", hue="Group", data=df, palette="PRGn")
    sns.despine(offset=10, trim=True)
    plt.show()

def rec_proed():
    # return pro-recovery and pro-ed users
    rec_users = rec_user('fed', 'scom')
    ed_users = proed_users('fed', 'scom')
    print len(rec_users), len(ed_users)
    print (set(ed_users).intersection(rec_users))
    return list(set(rec_users) - set(ed_users)), ed_users


def recovery_tweet():
    times = dbt.db_connect_col('fed', 'timeline')
    for tweet in times.find():
        text = tweet['text'].encode('utf8')
        text = text.strip().lower().replace("-", "").replace('_', '')
        sentences = re.split( r"\s*[;:`\"()?!{}]\s*|--+|\s*-\s+|''|\.\s|\.$|\.\.+|¡°|¡±", text )
        FLAG = False
        for sentence in sentences:
            if 'recover' in sentence:
                if 'not' not in sentence and 'don\'t' not in sentence and 'never' not in sentence \
                        and 'anti' not in sentence and 'non' not in sentence\
                        and 'relapse' not in sentence:
                    FLAG = True
            # if 'struggl' in sentence:
            #     if 'thin' not in sentence and 'weight' not in sentence \
            #             and 'mirror' not in sentence and 'figure' not in sentence \
            #             and 'food' not in sentence and 'body' not in sentence\
            #             and 'proed' not in sentence and 'proana' not in sentence and 'promia' not in sentence:
            #         FLAG = True
            # if 'fight' in sentence:
            #     if 'thin' not in sentence and 'weight' not in sentence \
            #             and 'mirror' not in sentence and 'figure' not in sentence \
            #             and 'food' not in sentence and 'body' not in sentence:
            #         FLAG = True
        # for sentence in sentences:
        #     if 'proed' in sentence or 'proana' in sentence or 'promia' in sentence:
        #         if 'not' not in sentence and \
        #                         'don\'t' not in sentence and \
        #                         'anti' not in sentence:
        #             FLAG = False
        if FLAG:
            print tweet['id'], ' '.join(tweet['text'].split()).encode('utf-8')


if __name__ == '__main__':
    # recovery_tweet()
    ed_users = rec_user('fed', 'scom')
    rec_users = proed_users('fed', 'scom')
    print len(ed_users), len(rec_users)
    print (set(ed_users).intersection(rec_users))



    # print 'Friendship'
    # network('fed', 'com', 'net')
    # types = ['retweet', 'reply', 'mention', 'communication', 'all']
    # for type in types:
    #     print type
    #     benetwork('fed', type, 'bnet')

    # rec_users = rec_user('fed', 'scom')
    # rec_users1 = rec_user('fed', 'com')
    # rec_users2 = rec_user('fed2', 'com')
    # print len(rec_users2)
    # print 'Common users', len(set(rec_users).intersection(set(rec_users1)))
    # print 'Common users', len(set(rec_users1).intersection(set(rec_users2)))
    # print rec_users


    '''Compare Pro-ED and Pro-recovery'''
    # rec_users1 = rec_user('fed', 'com')
    # print len(rec_users1)
    # ed_users = iot.get_values_one_field('fed', 'com', 'id', filt={'level':1})
    # pro_ed = list(set(ed_users)-set(rec_users1))
    # print len(pro_ed)
    # pickle.dump(rec_users1, open('data/pro-recovery.pick', 'w'))
    # pickle.dump(pro_ed, open('data/pro_ed.pick', 'w'))
    # rec_users1 = pickle.load(open('data/pro-recovery.pick', 'r'))
    # pro_ed = pickle.load(open('data/pro_ed.pick', 'r'))
    #
    # field = 'liwc_anal.result.ingest'
    # pro_rec_field = iot.get_values_one_field('fed', 'com', field, filt={'id':{'$in': rec_users1}})
    # pro_ed_field = iot.get_values_one_field('fed', 'com', field, filt={'id':{'$in': pro_ed}})
    # import seaborn as sns
    # import matplotlib.pyplot as plt
    # sns.distplot(pro_rec_field, label='Recovery user '+str(len(pro_rec_field)), hist=False)
    # sns.distplot(pro_ed_field, label='Non-Recovery user '+str(len(pro_ed_field)), hist=False)
    # # plt.xlabel(r'$\Delta$('+name+')')
    # # plt.ylabel(r'p($\Delta$)')
    # plt.legend()
    # plt.show()
    # distribution_change('fed', 'com')


    '''Print user profiles'''
    # print_user_profile('fed', 'scom')

    '''Pro ED and Recovery user network'''
    # pro_ed_rec_network('fed', 'scom', 'snet')


