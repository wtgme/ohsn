# -*- coding: utf-8 -*-
"""
Created on 14:58, 14/04/16

@author: wt
"""


def compare_id():
    bnets,  liwcs = set(), set()
    with open('ped-bnet.data', 'r') as f:
        for line in f.readlines():
            bnets.add(line.strip())
    with open('ped-liwc.data', 'r') as f:
        for line in f.readlines():
            liwcs.add(line.strip())

    print len(bnets), len(liwcs)
    print len(bnets.intersection(liwcs))
    for name in bnets.intersection(liwcs):
        print name

compare_id()
