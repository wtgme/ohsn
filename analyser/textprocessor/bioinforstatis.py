# -*- coding: utf-8 -*-
"""
Created on 16:00, 01/02/16

@author: wt

Conduct statistics on how much bio-information the data provides.
"""

from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbutil
import util.plot_util as plot


db = dbutil.db_connect_no_auth('fed')
ed_poi = db['poi']

biolist =   ['text_anal.gw.value',
              'text_anal.cw.value',
              # 'text_anal.edword_count.value',
              'text_anal.h.value',
              'text_anal.a.value',
              'text_anal.lw.value',
              'text_anal.hw.value']
all_count = ed_poi.count({})

print 'All count:', all_count
for name in biolist:
    count = ed_poi.count({name:{'$exists': True}})
    percent = float(count)/all_count
    print ('%s, %d, %.2f' % (name, count, percent))

count = ed_poi.count({"$or":[{biolist[0]:{'$exists': True}},
                     {biolist[1]:{'$exists': True}},
                     {biolist[2]:{'$exists': True}},
                     {biolist[3]:{'$exists': True}},
                     {biolist[4]:{'$exists': True}},
                     {biolist[5]:{'$exists': True}}]})
percent = float(count)/all_count
print ('Have any information, %d, %.2f' % (count, percent))

# for user in ed_poi.find({"$and":[{biolist[0]:{'$exists': False}},
#                      {biolist[1]:{'$exists': False}},
#                      {biolist[2]:{'$exists': False}},
#                      {biolist[3]:{'$exists': False}},
#                      {biolist[4]:{'$exists': False}},
#                      {biolist[5]:{'$exists': False}}]}):
#     print '----------------------------------------------'
#     print user['id'], user['screen_name'], user['description']

gws = []
cws = []
for user in ed_poi.find({
                         'text_anal.lw.value':{'$exists': False},
                         # 'text_anal.hw.value':{'$exists': True}
                        }):
    # value = user['text_anal']['lw']['value']
    # # value2 = user['text_anal']['hw']['value']
    # gws.append(value)
    # # cws.append(value2)
    print '-----------------------------------------------'
    print user['id'], user['screen_name'], user['description']
    # print '----', value

#
# for user in ed_poi.find({'text_anal.cw.value':{'$exists': True}}):
#     gws.append(user['text_anal']['cw']['value'])

# print min(gws), max(gws), len(gws)
# print min(cws), max(cws), len(cws)
# plot.pdf_plot_one_data(gws, 'height', 100, 200)
# plot.pdf_plot_one_data(cws, 'hw', 20, 200)
# plot.plot_pdf_two_data(gws, cws, 25, 200, 'lw', 'hw')