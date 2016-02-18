# -*- coding: utf-8 -*-
"""
Created on 13:56, 18/02/16

@author: wt

Compare the difference from their profile information
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbt
import pymongo
import networkx as nx
import util.plot_util as plot
import math


def get_field_values(db_name, field):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    counts = []
    for user in poi.find({'level': 1}, [field]):
        counts.append(user[field])
    return counts


def cate_color(colors):
    for color in colors:


get_field_values('fed', 'followers_count')
get_field_values('fed', 'friends_count')
get_field_values('fed', 'favourites_count')
get_field_values('fed', 'statuses_count')

