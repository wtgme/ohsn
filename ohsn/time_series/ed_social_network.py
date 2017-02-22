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


def output_net_user_data(dbname, comname, netname):
    '''
    Output the social network (two-ground) and user's ED states into local files
    '''
    net = dbt.db_connect_col(dbname, netname)
    fw = open(dbname+'-two-net.data', 'w')
    for record in net.find():
        # Edge is from FOLLOWER ----->>> USER
        fw.write(str(record['follower']) + '\t' + str(record['user']) + '\n')
    fw.flush()
    fw.close()

    com = dbt.db_connect_col(dbname, comname)
    fw = open(dbname+'-two-net-user.data', 'w')
    for record in com.find():
        ed_flag = profiles_check.check_ed(record)
        out = 0
        if ed_flag:
            out = 1
        fw.write(str(record['id']) + '\t' + str(out) + '\n')
    fw.flush()
    fw.close()


def user_tag(filename):
    '''
    Load users' ED states
    '''
    d = {}
    with open(filename, 'r') as f:
        for line in f:
            (key, val) = line.split()
            d[int(key)] = val
    return d


def friends_friends(dbname, comname, flag):
    '''
    Load the two-ground social networks, and users' ED states from local files
    Produce the numbers of ED friends, non-ED friends, ED friends' friends, non-ED friends' friends
    '''
    filter_user = {'level': 1}
    users = iot.get_values_one_field(dbname, comname, 'id', filter_user)
    net = gt.Graph.Read_Ncol(dbname+'-two-net.txt')
    com = user_tag(dbname+'-two-net-user.txt')
    data = []
    for uid in users:
        row = [uid, flag]
        exist = True
        try:
            v = net.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            friends = set([int(net.vs[v]['name']) for v in net.neighbors(str(uid))])
            ed_fri_num, noned_fri_num, ed_fri_fri_num, noned_fri_fri_num = 0, 0, 0, 0
            if len(friends) > 0:
                for fid in friends:
                    ed_flag = com.get(fid)
                    if ed_flag:
                        ed_fri_num += 1
                    else:
                        noned_fri_num += 1
                    fri_friends = set([int(net.vs[v]['name']) for v in net.neighbors(str(fid))])
                    row.extend([ed_fri_num, noned_fri_num])
                    if len(fri_friends) > 0:
                        for ffid in fri_friends:
                            ed_flag = com.get(ffid)
                            if ed_flag:
                                ed_fri_fri_num += 1
                            else:
                                noned_fri_fri_num += 1
                        row.extend([ed_fri_fri_num, noned_fri_fri_num])
                    else:
                       row.extend([None] * 2)
            else:
                row.extend([None] * 4)
        data.append(row)
    return data


def ed_friend_num(dbname, comname, netname, flag):
    '''
    Only one-round social network are used
    '''
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


def out_ed_social():
    '''
    out csv file on numbers of ED friends, non-ED friends, ED-friends-frineds, non-ED-friends-friends
    '''
    attr_names = ['uid', 'ed',
                  'ed_fr', 'non_ed_fr',
                  'ed_fr_fr', 'non_ed_fr_fr']
    print attr_names
    data = friends_friends('fed', 'com', '1')
    rd_data = friends_friends('random2', 'com', '0')
    data.extend(rd_data)
    df = pd.DataFrame(data, columns=attr_names)
    df.to_csv('data-ed-social.csv', index = False)

def out_ed_friend_num():
    '''
    out csv file for only one-round social network
    '''
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
    # out_ed_friend_num()
    # net = gt.load_network('fed', 'net')
    # net.write_graphml('ed-two-net.graphml')

    output_net_user_data(dbname='random2', comname='com', netname='net')




