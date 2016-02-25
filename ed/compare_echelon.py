# -*- coding: utf-8 -*-
"""
Created on 17:26, 21/01/16

@author: wt
Compare the common users in Echelon and Ed data set

"""
import sys
sys.path.append('..')
import util.db_util as dbt
from api import profiles_check

db = dbt.db_connect_no_auth('ed')
ed_poi = db['poi_ed']

# db = dbt.db_connect_no_auth('echelon')
ech_poi = db['poi_ed_all']

# Common users in Echelon and ED
# index = 1
# for poi in ed_poi.find({}):
#     poi_id = poi['id']
#     count = ech_poi.count({'id':poi_id})
#     if count > 0:
#         print index, poi_id, poi['screen_name']
#         index += 1

# Target users in Echelon but not in ED
index = 1
for poi in ech_poi.find({}):
    poi_id = poi['id']
    if profiles_check.check_ed(poi):
        count = ed_poi.count({'id':poi_id})
        if count < 1:
            print index, poi_id, poi['screen_name']
            index += 1
