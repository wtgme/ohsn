# -*- coding: utf-8 -*-
"""
Created on 12:59 PM, 3/1/16

@author: tw
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

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
            t = x.get(levels[0], {})
            for level in levels[1:]:
                # print level
                t = t.get(level)
                if t is None:
                    t = 0.0
                    break
            values.append(t)
        else:
            values.append(x.get(field))
    return values


def get_values_one_field(dbname, colname, fieldname, filt={}):
    poi = dbt.db_connect_col(dbname, colname)
    values = []
    for item in poi.find(filt, [fieldname], no_cursor_timeout=True):
        if '.' in fieldname:
            levels = fieldname.split('.')
            t = item.get(levels[0], {})
            for level in levels[1:]:
                t = t.get(level)
                if t is None:
                    t = 0.0
                    break

            values.append(t)
        else:
            values.append(item.get(fieldname))
    # print 'The length of values is: ', len(values)
    return values


def most_common(lst):
    return max(set(lst), key=lst.count)


def print_tweets(dbname, timeline):
    db = dbt.db_connect_no_auth(dbname)
    time = db[timeline]
    for tweet in time.find():
        try:
            print tweet['text']
        except UnicodeEncodeError:
            pass

if __name__ == '__main__':
    print_tweets('fed', 'stimeline')
