# -*- coding: utf-8 -*-
"""
Created on 16:49, 02/03/16

@author: wt
"""
import sys
sys.path.append('..')
from networkx import *
import util.net_util as nt
import util.plot_util as plot


DG = nt.load_network('yg', 'cnet')
# parts = community.best_partition(G_fb)
plot.plot_whole_network(DG)


