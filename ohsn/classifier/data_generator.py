# -*- coding: utf-8 -*-
"""
Created on 8:15 PM, 2/27/16

@author: tw
Export data from mongodb for classification and feature analysis
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.io_util as io
from ohsn.edrelated import edrelatedcom
from ohsn import prof as ic
import pickle
import urllib2


def image_main_color(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    poi = db[colname]
    color_list = {}
    index = 0
    for user in poi.find({'profile_banner_url': {'$exists': True},
                          'liwc_anal.result.WC': {'$exists': True}},
                         ['id', 'profile_banner_url']):
        uid = user['id']
        url = user['profile_banner_url']
        index += 1
        if index%100==0:
            print 'Have processed users:', index
        try:
            main_colors = ic.main_colors(url)
            color_list[uid] = main_colors
        except urllib2.HTTPError:
            continue
        # if len(color_list)>10000:
        #     break
    return color_list


def map_label_senti(labels):
    user_senti = {}
    csmap = ic.get_color_sent()
    print csmap
    for user in labels.keys():
        labs = labels[user]
        user_senti[user] = [csmap[lab] for lab in labs]
    return user_senti


def map_color_label(uimages):
    user_tags = {}
    stand = ic.color_wheel()
    for user in uimages.keys():
        colors = uimages[user]
        user_tags[user] = [ic.color_map(color, stand, cformat='lab') for color in colors]
        # print user, user_tags[user]
    return user_tags


def color_classify(userlabels, field_names, file_name, dbname):
    fw = open(file_name+'.data', 'w')
    db = dbt.db_connect_no_auth(dbname)
    poi = db['com']
    # format: 6,7,11,12 1:-0.022711 2:-0.050504 3:-0.035691
    for uid in userlabels.keys():
        labels = (userlabels[uid])
        user = poi.find_one({'id': uid}, ['liwc_anal.result'])
        values = io.get_fields_one_doc(user, field_names)
        outstr = ','.join(str(x) for x in labels)
        outstr += ' '
        for i in xrange(len(values)):
            outstr += str(i+1)+':'+str(values[i])+' '
        fw.write(outstr+'\n')
    fw.close()


def feature_output(field_names, file_name, dbname, label, outids=False, userset=[], extend_features={}):
    fw = open(file_name+'.data', 'a')
    db = dbt.db_connect_no_auth(dbname)
    poi = db['scom']
    index = 0
    maxsize = 10000000000000000
    uids = list()
    # exclude_set = set([4319191638L, 2627223434L, 2976822286L, 4788248335L, 3289264086L, 520847919, 439647015, 947539758, 617442479, 2481703728L, 2913311029L, 3760687289L, 2303011905L, 1712561862, 2882255303L, 261549132, 982895821, 2849269327L, 312684498, 160044558, 774072534, 330611545, 430569947, 1275228253, 3399616094L, 2924322143L, 457692129, 3006221026L, 2837359399L, 18942418, 2848241137L, 273768180, 235857269, 3315086840L])

    for x in poi.find({
                       # 'text_anal.edword_count.value': {'$gt': 0},
                       'id': {'$in': userset},
                       'liwc_anal.result.WC': {'$exists': True},
                        # 'text_anal.gbmi': {'$exists': True},
                       # 'timeline_count': {'$gt': 100},
                       # 'level': {'$gt': 1}
                       }):
        if index < maxsize:
            uid = int(x['id'])
            uids.append(uid)
            values = io.get_fields_one_doc(x, field_names)
            if uid in extend_features:
                values.extend(extend_features[uid])
            outstr = label + ' '
            for i in xrange(len(values)):
                outstr += str(i+1)+':'+str(values[i])+' '
            index += 1
            fw.write(outstr+'\n')
    fw.close()
    print len(uids)
    if outids:
        pickle.dump(uids, open(file_name+'_ids.data', 'w'))


def potential_users(dbname, comname):
    ed_users = edrelatedcom.ed_user(dbname, comname)
    rec_users = edrelatedcom.rec_user(dbname, comname)
    return list(set(ed_users).union(set(rec_users)))


if __name__ == '__main__':
    # ygimage = image_main_color('young', 'com')
    # pickle.dump(ygimage, open('data/ygimage.pick', 'w'))
    # ygimage = pickle.load(open('data/ygimage.pick', 'r'))
    # print len(ygimage)
    # labels = map_color_label(ygimage)
    # pickle.dump(labels, open('data/yglabels.pick', 'w'))
    # labels = pickle.load(open('data/yglabels.pick', 'r'))
    # print labels
    # senti = map_label_senti(labels)
    # pickle.dump(senti, open('data/ygsentis.pick', 'w'))
    # senti = pickle.load(open('data/ygsentis.pick', 'r'))
    # LIWC = io.read_fields()
    # print len(LIWC)
    # print len(senti)
    # print senti
    # color_classify(senti, LIWC, 'data/ygcolor', 'young')


    """Generate Data for user classification"""
    fields = io.read_fields()
    print len(fields)
    # common = pickle.load(open('data/common.pick', 'r'))
    # fields = LIWC[common]
    # print len(LIWC[common])
    # print fields
    #
    # # common users in random and young = set([4319191638L, 2627223434L, 2976822286L, 4788248335L, 3289264086L, 520847919, 439647015, 947539758, 617442479, 2481703728L, 2913311029L, 3760687289L, 2303011905L, 1712561862, 2882255303L, 261549132, 982895821, 2849269327L, 312684498, 160044558, 774072534, 330611545, 430569947, 1275228253, 3399616094L, 2924322143L, 457692129, 3006221026L, 2837359399L, 18942418, 2848241137L, 273768180, 235857269, 3315086840L])
    # # fed, random, young
    # users = potential_users('fed', 'com')

    # triangle = pickle.load(open('data/triangle.pick', 'r'))
    # print triangle


    # feature_output(fields, 'data/ed-rd', 'random', '-1', False, [])

    '''Generate Pro-ed and pro-recovery data'''
    import ohsn.edrelated.edrelatedcom as er
    ed_users = er.rec_user('fed', 'scom')
    rec_users = er.proed_users('fed', 'scom')
    common = set(ed_users).intersection(rec_users)
    ed_users = list(set(ed_users) - common)
    rec_users = list(set(rec_users) - common)
    print len(ed_users), len(rec_users)
    user_hash_profile = pickle.load(open('data/user-hash-profile.pick', 'r'))
    feature_output(fields, 'data/pro-ed-rec', 'fed', '1', False, rec_users, user_hash_profile)
    feature_output(fields, 'data/pro-ed-rec', 'fed', '-1', False, ed_users, user_hash_profile)


    # """Generate Data for GBMI regression"""
    # fields = io.read_fields()
    # feature_output(fields, 'data/gbmi', 'fed', '0', True)


