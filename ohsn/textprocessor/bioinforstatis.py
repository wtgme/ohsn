# -*- coding: utf-8 -*-
"""
Created on 16:00, 01/02/16

@author: wt

Conduct statistics on how much bio-information the data provides.
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import db_util as dbutil
from ohsn.util import plot_util as plot
from ohsn.util import io_util as iot
import pandas as pd
import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt


def bio_statis(dbname, colname):
    db = dbutil.db_connect_no_auth(dbname)
    bio = db[colname]
    biolist =    ['results.gw.value',
                  'results.cw.value',
                  'results.edword_count.value',
                  'results.h.value',
                  'results.a.value',
                  'results.lw.value',
                  'results.hw.value']

    for name in biolist:
        user_count = {}
        for rec in bio.find({name:{'$exists': True}}):
            count = user_count.get(rec['uid'], 0)
            count += 1
            user_count[rec['uid']] = count
        change_count = 0
        for user in user_count.keys():
            if user_count[user] > 1:
                change_count += 1
        # print user_count
        percent = float(len(user_count))/61580
        change_per = float(change_count)/len(user_count)
        print ('%s, %.2f, %.2f' % (name, percent, change_per))

    count = bio.count({"$or":[{biolist[0]:{'$exists': True}},
                         {biolist[1]:{'$exists': True}},
                         # {biolist[2]:{'$exists': True}},
                         {biolist[3]:{'$exists': True}},
                         # {biolist[4]:{'$exists': True}},
                         {biolist[5]:{'$exists': True}},
                         {biolist[6]:{'$exists': True}}]})
    print ('Have anyone, %.2f' %(float(count)/61580))

# bio_statis('fed', 'bio')


def verfy_change(dbname, bioname, timename):
    db = dbutil.db_connect_no_auth(dbname)
    bio = db[bioname]
    timeline = db[timename]

    for use in bio.find({'results.gw.value': {'$exists': True}}, ['uid']):
        uid = use['uid']
        print 'Processing current user:',  uid
        text = ''
        for time in timeline.find({'user.id': uid}, ['user.description']):
            if text != time['user']['description']:
                if text != '':
                    print time['user']['description']
                    print '-----------'
                text = time['user']['description']

# verfy_change('fed', 'bio', 'timeline')

def ed_bio_sta(dbname, colname):
    db = dbutil.db_connect_no_auth(dbname)
    ed_poi = db[colname]

    biolist =    ['text_anal.gw.value',
                  'text_anal.cw.value',
                  # 'text_anal.edword_count.value',
                  'text_anal.h.value',
                  'text_anal.a.value',
                  'text_anal.bmi.value',
                  'text_anal.cbmi.value',
                  'text_anal.gbmi.value',
                  'text_anal.lw.value',
                  'text_anal.hw.value']
    all_count = ed_poi.count({})

    print 'All count:', all_count
    for name in biolist:
        count = ed_poi.count({name:{'$exists': True}})
        percent = float(count)/all_count*100
        print ('%s, %d, %.2f' % (name, count, percent))

    # count = ed_poi.count({"$or":[{biolist[0]:{'$exists': True}},
    #                      {biolist[1]:{'$exists': True}},
    #                      {biolist[2]:{'$exists': True}},
    #                      {biolist[3]:{'$exists': True}},
    #                      {biolist[4]:{'$exists': True}},
    #                      {biolist[5]:{'$exists': True}}]})
    # percent = float(count)/all_count
    # print ('Have any information, %d, %.2f' % (count, percent))

    # for user in ed_poi.find({"$and":[{biolist[0]:{'$exists': False}},
    #                      {biolist[1]:{'$exists': False}},
    #                      {biolist[2]:{'$exists': False}},
    #                      {biolist[3]:{'$exists': False}},
    #                      {biolist[4]:{'$exists': False}},
    #                      {biolist[5]:{'$exists': False}}]}):
    #     print '----------------------------------------------'
    #     print user['id'], user['screen_name'], user['description']


def plot_bio(dbname, colname, fields, names):
    datas = list()
    for field in fields:
        datas.append(iot.get_values_one_field(dbname, colname, field, {field: {'$exists': True}}))
    plot.plot_pdf_mul_data(datas, 'Age', ['g-', 'b-', 'r-', 'k-'], ['s', 'o', '^', '*'],
                           names, linear_bins=True, central=True, fit=False, fitranges=None, savefile='bmi' + '.pdf')


def bmi_regreesion(dbname, colname, filename):
    # regress bmi with features
    fields = iot.read_fields()
    poi_fields = fields[-9:-1]
    print poi_fields
    trimed_fields = [(field.split('.')[-1]) for field in fields]
    trimed_fields[-10:] = ['sentiment', 'age', 'gender', 'height', 'cw',
                          'gw', 'cbmi', 'gbmi', 'edword', 'level']

    com = dbutil.db_connect_col(dbname, colname)
    data = []
    # for user in com.find({'$or': [{'text_anal.cbmi.value': {'$exists': True}},
    #                               {'text_anal.gbmi.value': {'$exists': True}}],
    #                       'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
    com2 = dbutil.db_connect_col('fed2', colname)
    com3 = dbutil.db_connect_col('fed3', colname)
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        values = iot.get_fields_one_doc(user, fields)
        user2 = com2.find_one({'id': user['id']})
        if user2:
            values.extend(iot.get_fields_one_doc(user2, poi_fields))
        else:
            values.extend([0]*len(poi_fields))
        user3 = com3.find_one({'id': user['id']})
        if user3:
            values.extend(iot.get_fields_one_doc(user3, poi_fields))
        else:
            values.extend([0]*len(poi_fields))
        data.append(values)
    df = pd.DataFrame(data, columns=trimed_fields + [(field.split('.')[-2] + '_p2') for field in poi_fields] +
                      [(field.split('.')[-2] + '_p3') for field in poi_fields])
    df.to_csv(filename)


if __name__ == '__main__':
    # ed_bio_sta('fed', 'scom')
    # fields = [
    #               # 'text_anal.gw.value',
    #               # 'text_anal.cw.value',
    #               # 'text_anal.edword_count.value',
    #               # 'text_anal.h.value',
    #               # 'text_anal.a.value',
    #               # 'text_anal.bmi.value',
    #               'text_anal.cbmi.value',
    #               'text_anal.gbmi.value',
    #               # 'text_anal.lw.value',
    #               # 'text_anal.hw.value'
    # ]
    # plot_bio('fed', 'scom', fields, ['CBMI', 'GBMI'])

    # bmi_regreesion('fed', 'com', 'data/bmi_reg.csv')

    fields = iot.read_fields()
    poi_fields = fields[-9:-1]
    print poi_fields
    trimed_fields = [(field.split('.')[-1]) for field in fields]
    trimed_fields[-10:] = ['sentiment', 'age', 'gender', 'height', 'cw',
                          'gw', 'cbmi', 'gbmi', 'edword', 'level']
    df = pd.read_csv('data/bmi_reg.csv', index_col=0)
    df.columns = trimed_fields + [(field.split('.')[-2] + '_p2') for field in poi_fields] + [(field.split('.')[-2] + '_p3') for field in poi_fields]
    df.to_csv('data/bmi_reg.csv')


