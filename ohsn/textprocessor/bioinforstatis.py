# -*- coding: utf-8 -*-
"""
Created on 16:00, 01/02/16

@author: wt

Conduct statistics on how much bio-information the data provides.
"""

from ohsn.util import db_util as dbutil
from ohsn.util import plot_util as plot


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
        percent = float(count)/all_count
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


def plot_bio(dbname, colname, w1, w2):
    db = dbutil.db_connect_no_auth(dbname)
    ed_poi = db[colname]
    gws = []
    cws = []
    for user in ed_poi.find({
                             'text_anal.'+w1+'.value':{'$exists': True},
                             'text_anal.'+w2+'.value':{'$exists': True}
                            }):
        value = user['text_anal'][w1]['value']
        value2 = user['text_anal'][w2]['value']
        gws.append(value)
        cws.append(value2)
        # print '-----------------------------------------------'
        # print  user['description']
        # print 'age', value, value2


    # for user in ed_poi.find({'text_anal.cw.value':{'$exists': True}}):
    #     gws.append(user['text_anal']['cw']['value'])

    print min(gws), max(gws), len(gws)
    print min(cws), max(cws), len(cws)
    # plot.pdf_plot_one_data(gws, 'height', 100, 200)
    # plot.pdf_plot_one_data(cws, 'hw', 20, 200)
    # plot.plot_pdf_mul_data(gws, cws, 25, 200, 'lw', 'hw')
    plot.plot_pdf_mul_data([gws, cws], ['--bo', '--r^'], 'GCW',  ['HW', 'LW'], True)



if __name__ == '__main__':
    # ed_bio_sta('fed', 'scom')
    plot_bio('fed', 'scom', 'hw', 'lw')
