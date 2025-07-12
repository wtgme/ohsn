import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import pymongo
from ohsn.util import db_util as dbt
from datetime import datetime
import numpy as np
import pandas as pd
import pickle
import ohsn.util.io_util as iot
from lifelines.utils import datetimes_to_durations
import ohsn.util.graph_util as gt
import scipy.stats as stats


def active_users():
    time2 = dbt.db_connect_col('fed2', 'com')
    time3 = dbt.db_connect_col('fed3', 'com')
    time4 = dbt.db_connect_col('fed4', 'com')
    user_periods = {}
    for i, time in enumerate([time2, time3, time4]):
        for user in time.find({ "timeline_count": {'$gt': 0}}, ['id'], no_cursor_timeout=True):
            # if user['timeline_count'] > 0:
            periods = user_periods.get(user['id'], [])
            periods.append(i+1)
            user_periods[user['id']] = periods
    pickle.dump(user_periods, open('fed_active_periods.pick', 'w'))


if __name__ == '__main__':
    active_users()