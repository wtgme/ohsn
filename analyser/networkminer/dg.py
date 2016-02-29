# -*- coding: utf-8 -*-
"""
Created on 5:56 PM, 11/4/15

@author: wt

"""
import sys
sys.path.append('..')
from networkx import *
import matplotlib.pyplot as plt
import csv
import util.db_util as dbt


# load a network from file (directed weighted network)
def load_network(db_name, collection):
    DG = DiGraph()
    db = dbt.db_connect_no_auth(db_name)
    cols = db[collection]
    for row in cols.find({}):
        n1 = row['user']
        n2 = row['follower']
        weightv = 1
        if (DG.has_node(n1)) and (DG.has_node(n2)) and (DG.has_edge(n1, n2)):
            DG[n1][n2]['weight'] += weightv
        else:
            DG.add_edge(n1, n2, weight=weightv)
    return DG


def get_adjacency_matrix(DG):
    A = adjacency_matrix(DG, weight=None)  # degree matrix, i.e. 1 or 0
    #A = adjacency_matrix(DG)  # strength matrix, i.e., the number of edge
    return A


def out_adjacency_matrix(DG):
    A = adjacency_matrix(DG, weight=None)  # degree matrix, i.e. 1 or 0
    #A = adjacency_matrix(DG)  # strength matrix, i.e., the number of edge
    Ade = A.todense()
    Nlist = map(int, DG.nodes())
    print len(Nlist)
    with open('degree_adjacency_matrix.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([0]+Nlist)
        for index in xrange(len(Nlist)):
            spamwriter.writerow([Nlist[index]] + Ade[index].getA1().tolist())


def plot_whole_network(DG):
    # pos = random_layout(DG)
    # pos = shell_layout(DG)
    pos = spring_layout(DG)
    # pos = circular_layout(DG)
    # pos = fruchterman_reingold_layout(DG)
    # pos = spectral_layout(DG)
    # plt.title('Plot of Network')
    draw(DG, pos)
    plt.show()


def neibors_static(DG, node, neib='pre', direct='in', weight=False):
    if neib == 'suc':
        neibors = DG.successors(node)
    else:
        neibors = DG.predecessors(node)
    if direct == 'out':
        if weight:
            values = [DG.out_degree(n, weight='weight') for n in neibors]
        else:
            values = [DG.out_degree(n) for n in neibors]
    else:
        if weight:
            values = [DG.in_degree(n, weight='weight') for n in neibors]
        else:
            values = [DG.in_degree(n) for n in neibors]
    if len(neibors):
        return float(sum(values))/len(neibors)
    else:
        return 0.0


# network analysis
DG = load_network('ed2', 'net_ed')
print 'The number of nodes: %d' %(DG.order())
print 'The number of nodes: %d' %(DG.__len__())
print 'The number of nodes: %d' %(DG.number_of_nodes())
print 'The number of edges: %d' %(DG.size())
print 'The number of self-loop: %d' %(DG.number_of_selfloops())

# plot_whole_network(DG)
# plot_whole_network(DG)

# G = DG.to_undirected()
# print 'Network is connected:', (nx.is_connected(G))
# print 'The number of connected components:', (nx.number_connected_components(G))
# largest_cc = max(nx.connected_components(G), key=len)
#
#
# for node in DG.nodes():
#     if node not in largest_cc:
#         DG.remove_node(node)

print 'The plot of in-degree and out-degree of nodes'
print 'Node \t In \t Out \t In+Out'
indegree, outdegree, instrength, outstrength = [],[],[],[]
suc_in_d, suc_out_d, pre_in_d, pre_out_d = [], [], [], []
suc_in_s, suc_out_s, pre_in_s, pre_out_s = [], [], [], []


for node in DG.nodes():
    # print 'Degree: %s \t %d \t %d \t %d' %(node, DG.in_degree(node), DG.out_degree(node), DG.degree(node))
    # print 'Strength: %s \t %d \t %d \t %d' %(node, DG.in_degree(node, weight='weight'), DG.out_degree(node, weight='weight'), DG.degree(node, weight='weight'))
    in_d, out_d, in_s, out_s = DG.in_degree(node), DG.out_degree(node), DG.in_degree(node, weight='weight'), DG.out_degree(node, weight='weight')
    if in_d and out_d:
        indegree.append(in_d)
        outdegree.append(out_d)
        instrength.append(in_s)
        outstrength.append(out_s)
        # print 'node',node,'indegree', in_d, 'outdegree', out_d
        suc_in_d.append(neibors_static(DG, node, 'suc', 'in', False))
        suc_out_d.append(neibors_static(DG, node, 'suc', 'out', False))
        pre_in_d.append(neibors_static(DG, node, 'pre', 'in', False))
        pre_out_d.append(neibors_static(DG, node, 'pre', 'out', False))

        suc_in_s.append(neibors_static(DG, node, 'suc', 'in', True))
        suc_out_s.append(neibors_static(DG, node, 'suc', 'out', True))
        pre_in_s.append(neibors_static(DG, node, 'pre', 'in', True))
        pre_out_s.append(neibors_static(DG, node, 'pre', 'out', True))

# plot.pdf_plot(indegree, 'indegree', 100, 1000)
# plot.pdf_plot_one_data(indegree, 'indegree', min(indegree), max(indegree))

# plot.dependence(indegree, outdegree, '$k_o(k_i)$', 'indegree', 'outdegree', 1, 300)
# plot.dependence(outdegree, indegree, '$k_i(k_o)$', 'outdegree', 'indegree')
# plot.dependence(instrength, outstrength, '$s_o(s_i)$', 'instrength', 'outstrength', 50, 1700)
# plot.dependence(outstrength, instrength, '$s_i(s_o)$', 'outstrength', 'instrength')

# plot.dependence(indegree, pre_in_d, '$k_{i}^{pre}(k_i)$', 'indegree', 'Avg. Indegree of predecessors', 50)
# plot.dependence(indegree, pre_out_d, '$k_{o}^{pre}(k_i)$', 'indegree', 'Avg. Outdegree of predecessors', 50)
# plot.dependence(indegree, suc_in_d, '$k_{i}^{suc}(k_i)$', 'indegree', 'Avg. Indegree of successors', 50)
# plot.dependence(indegree, suc_out_d, '$k_{o}^{suc}(k_i)$', 'indegree', 'Avg. Outdegree of successors', 50)

# plot.dependence(outdegree, pre_in_d, '$k_{i}^{pre}(k_o)$', 'outdegree', 'Avg. Indegree of predecessors', 50)
# plot.dependence(outdegree, pre_out_d, '$k_{o}^{pre}(k_o)$', 'outdegree', 'Avg. Outdegree of predecessors', 50)
# plot.dependence(outdegree, suc_in_d, '$k_{i}^{suc}(k_o)$', 'outdegree', 'Avg. Indegree of successors', 50)
# plot.dependence(outdegree, suc_out_d, '$k_{o}^{suc}(k_o)$', 'outdegree', 'Avg. Outdegree of successors', 50)

# plot.dependence(instrength, pre_in_s, '$s_{i}^{pre}(s_i)$', 'Instrength', 'Avg. instrength of predecessors', 50)
# plot.dependence(instrength, pre_out_s, '$s_{o}^{pre}(s_i)$', 'Instrength', 'Avg. outstrength of predecessors', 50)
# plot.dependence(instrength, suc_in_s, '$s_{i}^{suc}(s_i)$', 'Instrength', 'Avg. instrength of successors', 50)
# plot.dependence(instrength, suc_out_s, '$s_{o}^{suc}(s_i)$', 'Instrength', 'Avg. outstrength of successors', 50)

# plot.dependence(outstrength, pre_in_d, '$s_{i}^{pre}(s_o)$', 'Outstrength', 'Avg. instrength of predecessors', 50)
# plot.dependence(outstrength, pre_out_d, '$s_{o}^{pre}(s_o)$', 'Outstrength', 'Avg. outstrength of predecessors', 50)
# plot.dependence(outstrength, suc_in_d, '$s_{i}^{suc}(s_o)$', 'Outstrength', 'Avg. instrength of successors', 50)
# plot.dependence(outstrength, suc_out_d, '$s_{o}^{suc}(s_o)$', 'Outstrength', 'Avg. outstrength of successors', 50)



# print 'pearson correlation of indegree and outdegree: %f' %(pearson(indegree, instrength))
# print 'pearson correlation of instrength and outstrength: %f' %(pearson(outdegree, outstrength))
#
# print 'radius: %d' %(radius(DG))
# print 'diameter: %d' %(diameter(DG))
# print 'eccentricity: %s' %(eccentricity(DG))
# print 'center: %s' %(center(DG))
# print 'periphery: %s' %(periphery(DG))
# print 'density: %s' %(density(DG))

# klist, plist = pmd(instrength)
# fit = powerlaw.Fit(instrength)
# print 'powerlaw lib fit'
# print fit.alpha
# figPDF = powerlaw.plot_pdf(instrength, color='b')
# powerlaw.plot_pdf(instrength, linear_bins=True, color='r', ax=figPDF)
# figPDF.scatter(klist, plist, c='k', s=50, alpha=0.4,marker='+', label='Raw')
# plt.show()