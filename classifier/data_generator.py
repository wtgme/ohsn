# -*- coding: utf-8 -*-
"""
Created on 8:15 PM, 2/27/16

@author: tw
Export data from mongodb for classification and feature analysis
"""
import sys
sys.path.append('..')
import util.db_util as dbt
import util.io_util as io
import prof.image_color as ic
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


def map_color_label(uimages):
    user_tags = {}
    for user in uimages.keys():
        colors = uimages[user]


def liwc_feature_output(field_names, file_name, dbname, label, outids=False):
    fw = open(file_name+'.data', 'a')
    db = dbt.db_connect_no_auth(dbname)
    poi = db['com']
    index = 0
    maxsize = 10000000000000000
    uids = list()
    # exclude_set = set([4319191638L, 2627223434L, 2976822286L, 4788248335L, 3289264086L, 520847919, 439647015, 947539758, 617442479, 2481703728L, 2913311029L, 3760687289L, 2303011905L, 1712561862, 2882255303L, 261549132, 982895821, 2849269327L, 312684498, 160044558, 774072534, 330611545, 430569947, 1275228253, 3399616094L, 2924322143L, 457692129, 3006221026L, 2837359399L, 18942418, 2848241137L, 273768180, 235857269, 3315086840L])

    for x in poi.find({'liwc_anal.result.WC': {'$exists': True},
                       # 'timeline_count': {'$gt': 100},
                       'level': {'$gt': 1}
                       },
                      ['id', 'liwc_anal.result']):
        if index < maxsize:
            if outids:
                label = str(index+1)
                uids.append(int(x['id']))
            values = io.get_fields_one_doc(x, field_names)
            outstr = label + ' '
            for i in xrange(len(values)):
                outstr += str(i+1)+':'+str(values[i])+' '
            index += 1
            fw.write(outstr+'\n')
    fw.close()
    if outids:
        pickle.dump(uids, open(file_name+'_ids.data', 'w'))


# ygimage = image_main_color('young', 'com')
# print len(ygimage)
# pickle.dump(ygimage, open('data/ygimage.pick', 'w'))
ygimage = pickle.load(open('data/ygimage.pick', 'r'))

# LIWC = io.read_fields()
# common = pickle.load(open('data/common.pick', 'r'))
# fields = LIWC[common]
# print len(LIWC[common])
# print fields
#
# # common users in random and young = set([4319191638L, 2627223434L, 2976822286L, 4788248335L, 3289264086L, 520847919, 439647015, 947539758, 617442479, 2481703728L, 2913311029L, 3760687289L, 2303011905L, 1712561862, 2882255303L, 261549132, 982895821, 2849269327L, 312684498, 160044558, 774072534, 330611545, 430569947, 1275228253, 3399616094L, 2924322143L, 457692129, 3006221026L, 2837359399L, 18942418, 2848241137L, 273768180, 235857269, 3315086840L])
# # fed, random, young
# liwc_feature_output(fields, 'data/test', 'fed', '', True)


