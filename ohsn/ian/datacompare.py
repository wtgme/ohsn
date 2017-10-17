# -*- coding: utf-8 -*-
"""
Created on 14:30, 17/10/17

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pymongo
import ohsn.api.profiles_check as pck

def filter_user():
    # filter ED users from Ian data
    conn = dbt.db_connect_no_auth_ian()
    iandb = conn.connect('TwitterProAna')
    ianusers = iandb['users']
    for u in ianusers.find({}, no_cursor_timeout=True):
        if 'description' in u:
            text = u['description']
            if text != None and pck.check_ed_profile(text):
                print u['id']
        else:
            if 'history' in u:
                hists = u['history']
                for h in hists:
                    if 'description' in h:
                        text = h['description']
                        if text != None and pck.check_ed_profile(text):
                            print u['id']
    conn.disconnect()

def overlap():
    # overlap between two data
    core_ed = set(iot.get_values_one_field('fed', 'scom', 'id'))
    ian_ed = set()
    with open('uid.txt', 'r') as fo:
        for line in fo.readline():
            ian_ed.add(int(line.strip()))
    print len(core_ed), len(ian_ed), len(core_ed.intersection(ian_ed))


if __name__ == '__main__':
    # filter_user()
    overlap()