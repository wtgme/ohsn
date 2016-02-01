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


db = dbutil.db_connect_no_auth('echelon')
ed_poi = db['poi']

biolist =   ['text_anal.gw.value',
              'text_anal.cw.value',
              # 'text_anal.edword_count.value',
              'text_anal.h.value',
              'text_anal.a.value',
              'text_anal.lw.value',
              'text_anal.hw.value']
all_count = ed_poi.count({})

for name in biolist:
    print name ,ed_poi.count({name:{'$exists': True}}), ed_poi.count({name:{'$exists': True}})/float(all_count)