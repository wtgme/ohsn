# -*- coding: utf-8 -*-
"""
Created on 20:38, 01/11/16

@author: wt
Runner for all processing
"""

import ohsn.lexiconsmaster.liwc_timeline_processor as liwcp
import ohsn.networkminer.timeline_network_miner as netp
import ohsn.textprocessor.description_miner as textp
import ohsn.prof.profile_stat as engagement
import ohsn.prof.behavior_tweet_types as bpro
import ohsn.prof.behavior_net as bent


dbname = 'fed'
comname = 'com'
timename = 'timeline'

liwcp.process_db(dbname, comname, timename, 'liwc_anal')
netp.process_db(dbname, comname, timename, 'bnet', 10000)
textp.process_poi(dbname, comname)
engagement.gagement(dbname, comname)
bpro.beh_pro(dbname, comname, timename)
bent.inter_entropy(dbname, comname, timename)

