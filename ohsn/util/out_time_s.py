# -*- coding: utf-8 -*-
"""
Created on 4:01 PM, 4/26/16

@author: tw
"""
import db_util as dbt

db = dbt.db_connect_no_auth('fed')
for i in range(1, 6):
    colname = 'com_t'+str(i)
