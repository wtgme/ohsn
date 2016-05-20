# -*- coding: utf-8 -*-
"""
Created on 12:59 PM, 3/1/16

@author: tw
"""

from ohsn.util import db_util as dbt
import numpy as np
import os
import plot_util as splot


def read_fields(split=False):
    # read feature names in use
    MYDIR = os.path.dirname(__file__)
    fileds = []
    with open(os.path.join(MYDIR, 'fieldx.txt'), 'r') as fo:
        for line in fo.readlines():
            if not line.startswith(' '):
                line = line.strip()
                if split:
                    line = line.split('.')[-1]
                fileds.append(line)
    return np.array(fileds)


def get_fields_one_doc(x, fields):
    values = []
    for field in fields:
        if '.' in field:
            levels = field.split('.')
            t = x.get(levels[0])
            for level in levels[1:]:
                t = t.get(level)
            values.append(t)
        else:
            values.append(x.get(field))
    return values


def get_values_one_field(dbname, colname, fieldname, filt={}):
    poi = dbt.db_connect_col(dbname, colname)
    values = []
    for item in poi.find(filt, [fieldname], no_cursor_timeout=True):
        values.append(item[fieldname])
    return values


def get_field_values(db_name, colname, field):
    db = dbt.db_connect_no_auth(db_name)
    poi = db[colname]
    counts = []
    for user in poi.find({'level': 1}, [field]):
        counts.append(user[field])
    return counts


def get_mlvs_field_values(db_name, flag, field):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    counts = []
    tag_names = field.split('.')
    for v in poi.find({'level': 1, flag: {'$exists': True}}, [field]):
        # print v
        counts.append(v[tag_names[0]][tag_names[1]])
    return counts

def get_mlvs_field_values_uids(db_name, uids, flag, field):
    db = dbt.db_connect_no_auth(db_name)
    poi = db['com']
    counts = []
    tag_names = field.split('.')
    for uid in uids:
        v = poi.find_one({'id': uid, flag: {'$exists': True}}, [field])
        if v is None:
            continue
        else:
            counts.append(v[tag_names[0]][tag_names[1]])
    return counts


def get_sublevel_values(results, field):
    values = []
    for result in results:
        values.append(result[field])
    return values


def most_common(lst):
    return max(set(lst), key=lst.count)

