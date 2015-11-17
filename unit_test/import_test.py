__author__ = 'wt'

import os
import math
import sys

def test_networkx():
    try:
        import networkx as nx
    except ImportError:
        print('Could not import networkx')
        return None
    G = nx.Graph()
    G.add_edge(1, 3, weight=3)
    G.add_edge(1, 4, weight=4)
    assert G.nodes(data=True)
    print('Networkx OK')

def test_numpy():
    try:
        import numpy as np
    except ImportError:
        print('Could not import numpy')
        return None
    a = np.array(1, 2, 3)
    assert len(a)
    print('Numpy OK')

if __name__ == '__main__':
    print('Test Networkx')
    test_networkx()

    print('Test Numpy')
    test_numpy()