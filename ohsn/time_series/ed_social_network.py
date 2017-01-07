# -*- coding: utf-8 -*-
"""
Created on 15:26, 06/01/17

@author: wt

This script is to explore that ED friends would lead to users having ED.

"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


from ohsn.util import db_util as dbt
from ohsn.util import io_util as iot
from ohsn.api import profiles_check
from ohsn.util import graph_util as gt
import pandas as pd


def ed_friend_num(dbname, comname, netname, flag):
    filter_user = {'level': 1}
    users = iot.get_values_one_field(dbname, comname, 'id', filter_user)
    net = gt.load_network(dbname, netname)
    com = dbt.db_connect_col(dbname, comname)
    data = []
    for uid in users:
        row = [uid, flag]
        exist = True
        try:
            v = net.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            followees = set([int(net.vs[v]['name']) for v in net.successors(str(uid))])
            followers = set([int(net.vs[v]['name']) for v in net.predecessors(str(uid))])
            common = followees.intersection(followers)
            followees = followees - common
            followers = followers - common
            for fids in [followees, followers, common]:
                if len(fids) > 0:
                    print uid in fids
                    print len(fids)
                    ed_num, noned_num = 0, 0
                    for fid in fids:
                        ed_flag = profiles_check.check_ed(com.find_one({'id': fid}))
                        if ed_flag:
                            ed_num += 1
                        else:
                            noned_num += 1
                    row.extend([ed_num, noned_num])
                else:
                    row.extend([None] * 2)
        data.append(row)
    return data

def out_ed_friend_num():
    attr_names = ['uid', 'ed',
                  'ed_fr', 'non_ed_fr',
                  'ed_fo', 'non_ed_fo',
                  'ed_co', 'non_ed_co']
    print attr_names
    data = ed_friend_num('fed', 'com', 'net', '1')
    rd_data = ed_friend_num('random2', 'com', 'net', '0')
    data.extend(rd_data)
    df = pd.DataFrame(data, columns=attr_names)
    df.to_csv('data-ed-social.csv', index = False)


if __name__ == '__main__':
    out_ed_friend_num()


