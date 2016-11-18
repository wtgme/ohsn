# -*- coding: utf-8 -*-
"""
Created on 18:12, 14/08/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import db_util as dbt
import matplotlib.pyplot as plt
import pickle
import pandas as pd


def timeline(dbname, timename):
    db = dbt.db_connect_no_auth(dbname)
    timeline = db[timename]
    dates = []
    for status in timeline.find(no_cursor_timeout=True):
        dates.append(status['created_at'])
    return dates

if __name__ == '__main__':
    # dates = timeline('depression', 'search')
    # pickle.dump(dates, open('data/date.pick', 'w'))
    dates = pickle.load(open('data/date.pick', 'r'))
    # plot_time(dates, length=1, title='Depression')

    ts = pd.Series(dates)
    print ts.groupby(ts.dt.date).count()
    ts.groupby(ts.dt.date).count().plot()
    plt.show()