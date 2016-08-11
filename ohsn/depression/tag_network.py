# -*- coding: utf-8 -*-
"""
Created on 9:13 PM, 8/11/16

@author: tw
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.graph_util as gt


def tag_record(dbname, colname):
    db = dbt.db_connect_no_auth(dbname)
    col = db[colname]
    for

