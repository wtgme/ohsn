# -*- coding: utf-8 -*-
"""
Created on 5:56 PM, 11/4/15

@author: wt

"""
import sys
sys.path.append('..')
from networkx import *
import math
import matplotlib.pyplot as plt
import numpy as np
import csv
from sklearn.metrics import mean_squared_error
import os




# load a network from file (directed weighted network)
def load_network():
    DG = DiGraph()
    # /data/reference/sample_reply_mention.csv
    # /data/echelon/mrredges-no-tweet-no-retweet-poi-counted.csv
    # file_path = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-1])+'/data/reference/sample_reply_mention.csv'
    file_path = '../data/ed/ed_net.csv'
    print file_path
    with open(file_path, 'rt') as fo:
        reader = csv.reader(fo)
        first_row = next(reader)
        for row in reader:
            n1 = (row[1])
            n2 = (row[0])
            # b_type = row[2]
            weightv = 1
            # reply-to mentioned
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


def load_poi():
    # Get profiles of all users
    poi = {}
    file_path = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-1])+'/data/ed/ed_poi.csv'
    f = open(file_path, 'rb')
    reader = csv.reader(f, lineterminator='\n')
    first_row = next(reader)
    for row in reader:
        des = row[3]
        row[3] = des.replace('\n', ' ').replace('\r', ' ').replace('\r\n', ' ').replace('\n\r', ' ')
        # print '-------------'
        # print row[3]
        poi[row[0]] = row
    # return the description in the FIRST row and contents
    return (first_row, poi)


def out_targted_poi(DG):
    # print 'Output poi in DG network'
    Nlist = map(int, DG.nodes())
    print len(Nlist)
    first_row, poi = load_poi()
    csvfile = open('targeted-poi.csv', 'wb')
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(first_row)
    for index in xrange(len(Nlist)):
        # print poi.get(str(Nlist[index]))
        spamwriter.writerow(poi.get(str(Nlist[index]), None))


def plot_whole_network(DG):
    # pos = random_layout(DG)
    # pos = shell_layout(DG)
    pos = spring_layout(DG)
    # pos = spectral_layout(DG)
    # plt.title('Plot of Network')
    draw(DG, pos)
    plt.show()



def pdf(data, xmin=None, xmax=None, linear_bins=False, **kwargs):
    if not xmax:
        xmax = max(data)
    if not xmin:
        xmin = min(data)
    if linear_bins:
        bins = range(int(xmin), int(xmax))
    else:
        log_min_size = np.log10(xmin)
        log_max_size = np.log10(xmax)
        number_of_bins = np.ceil((log_max_size-log_min_size)*10)
        bins = np.unique(
                np.floor(
                    np.logspace(
                        log_min_size, log_max_size, num=number_of_bins)))
    hist, edges = np.histogram(data, bins, density=True)
    bin_centers = (edges[1:]+edges[:-1])/2.0
    new_x, new_y = [], []
    for index in xrange(len(hist)):
        if hist[index] != 0:
            new_x.append(bin_centers[index])
            new_y.append(hist[index])
    return new_x, new_y

def pearson(x, y):
    # calculate the pearson correlation of two list
    n = len(x)
    avg_x = float(sum(x))/n
    avg_y = float(sum(y))/n
    print 'The means of two lists:', avg_x, avg_y
    diffprod = 0.0
    xdiff2 = 0.0
    ydiff2 = 0.0
    for idx in range(n):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff*ydiff
        xdiff2 += xdiff*xdiff
        ydiff2 += ydiff*ydiff
    return diffprod/math.sqrt(xdiff2*ydiff2)


def drop_zeros(list_a):
    # discard the zeros in a list
    return [i for i in list_a if i>0]


def rmse(predict, truth):
    # calculate RMSE of a prediction
    RMSE = mean_squared_error(truth, predict)**0.5
    return RMSE


def mean_bin(list_x, list_y, linear_bins=False):
    # the returned values are raw values, not logarithmic values
    size = len(list_x)
    xmin = min(list_x)
    xmax = max(list_x)
    if linear_bins:
        bins = range(int(xmin), int(xmax+1))
    else:
        log_min_size = np.log10(xmin)
        log_max_size = np.log10(xmax+1)
        number_of_bins = np.ceil((log_max_size-log_min_size)*10)
        bins = np.unique(
                np.floor(
                    np.logspace(
                        log_min_size, log_max_size, num=number_of_bins)))

    new_bin_meanx_x, new_bin_means_y = [], []
    hist_x = np.histogram(list_x, bins)[0]
    hist_x_w = np.histogram(list_x, bins, weights=list_x)[0].astype(float)
    for index in xrange(len(bins)-1):
        if hist_x[index] != 0:
            new_bin_meanx_x.append(hist_x_w[index]/hist_x[index])
            range_min, range_max = bins[index], bins[index+1]
            sum_y = 0.0
            for i in xrange(size):
                key = list_x[i]
                if (key >= range_min) and (key < range_max):
                    sum_y += list_y[i]
            new_bin_means_y.append(sum_y/hist_x[index])
    return new_bin_meanx_x, new_bin_means_y


def cut_lists(list_x, list_y, fit_start=-1, fit_end=-1):
    if fit_start != -1:
        new_x, new_y = [], []
        for index in xrange(len(list_x)):
            if list_x[index] >= fit_start:
                new_x.append(list_x[index])
                new_y.append(list_y[index])
        list_x, list_y = new_x, new_y
    if fit_end != -1:
        new_x, new_y = [], []
        for index in xrange(len(list_x)):
            if list_x[index] < fit_end:
                new_x.append(list_x[index])
                new_y.append(list_y[index])
        list_x, list_y = new_x, new_y
    return (list_x, list_y)


def lr_ls(list_x, list_y, fit_start=-1, fit_end=-1):
    list_x, list_y = cut_lists(list_x, list_y, fit_start, fit_end)
    X = np.asarray(list_x, dtype=float)
    Y = np.asarray(list_y, dtype=float)
    logX = np.log10(X)
    logY = np.log10(Y)
    coefficients = np.polyfit(logX, logY, 1)
    polynomial = np.poly1d(coefficients)
    print 'Polynomial: (', fit_start, fit_end, ')',  polynomial
    logY_fit = polynomial(logX)
    print 'Fitting RMSE(log)', rmse(logY, logY_fit)
    print 'Fitting RMSE(raw)', rmse(Y, np.power(10, logY_fit))
    # print Y
    return (list_x, np.power(10, logY_fit))
    # return logX, logY_fit


def lr_ml(list_x, list_y, fit_start=-1, fit_end=-1):
    # TODO
    list_x, list_y = cut_lists(list_x, list_y, fit_start, fit_end)
    X = np.asarray(list_x, dtype=float)
    Y = np.asarray(list_y, dtype=float)
    logX = np.log10(X)
    logY = np.log10(Y)


def lr_ks(list_x, list_y, fit_start=-1, fit_end=-1):
    # TODO
    list_x, list_y = cut_lists(list_x, list_y, fit_start, fit_end)
    X = np.asarray(list_x, dtype=float)
    Y = np.asarray(list_y, dtype=float)
    logX = np.log10(X)
    logY = np.log10(Y)


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


def dependence(listx, listy, l, xlabel, ylabel, start=1, end=1000):
    plt.clf()
    plt.scatter(listx, listy, s=20, c='#fee8c8', marker='+', label='raw '+l)
    ax = plt.gca()
    xmeans, ymeans = mean_bin(listx, listy)
    ax.scatter(xmeans, ymeans, s=50, c='#fdbb84', marker='o', label='binned '+l)
    xfit, yfit = lr_ls(xmeans, ymeans, start, end)
    ax.plot(xfit, yfit, c='#e34a33', linewidth=2, linestyle='--', label='Fitted '+l)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_xlim(xmin=1)
    ax.set_ylim(ymin=1)
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=4)
    leg.draw_frame(True)
    plt.show()


'''Plot PDF'''
def pdf_plot(data, name, fit_start, fit_end):
    # plt.gcf()
    # data = outstrength
    list_x, list_y = pdf(data, linear_bins=True)
    plt.plot(list_x, list_y, 'r+', label='Raw '+name)
    ax = plt.gca()
    list_x, list_y = pdf(data)
    ax.plot(list_x, list_y, 'ro', label='Binned '+name)
    # list_fit_x, list_fit_y = lr_ls(list_x, list_y, 1, 100)
    # ax.plot(list_fit_x, list_fit_y, 'b--', label='Fitted outstrength')
    list_fit_x, list_fit_y = lr_ls(list_x, list_y, fit_start, fit_end)
    ax.plot(list_fit_x, list_fit_y, 'b--', label='Fitted '+name)
    # data = outstrength
    # list_x, list_y = pdf(data, linear_bins=True)
    # ax.plot(list_x, list_y, 'b+', label='Raw outstrength')
    # ax = plt.gca()
    # list_x, list_y = pdf(data)
    # ax.plot(list_x, list_y, 'bo', label='Binned outstrength')
    # list_fit_x, list_fit_y = lr_ls(list_x, list_y, 50)
    # ax.plot(list_fit_x, list_fit_y, 'b--', label='Fitted outstrength')
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    ax.set_xlim(xmin=1)
    ax.set_ylim(ymax=1)
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc=0)
    leg.draw_frame(True)
    plt.show()

# network analysis
DG = load_network()
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

# pdf_plot(indegree, 'indegree', 100, 1000)

# dependence(indegree, outdegree, '$k_o(k_i)$', 'indegree', 'outdegree', 1, 300)
# dependence(outdegree, indegree, '$k_i(k_o)$', 'outdegree', 'indegree')
# dependence(instrength, outstrength, '$s_o(s_i)$', 'instrength', 'outstrength', 50, 1700)
# dependence(outstrength, instrength, '$s_i(s_o)$', 'outstrength', 'instrength')

# dependence(indegree, pre_in_d, '$k_{i}^{pre}(k_i)$', 'indegree', 'Avg. Indegree of predecessors', 50)
# dependence(indegree, pre_out_d, '$k_{o}^{pre}(k_i)$', 'indegree', 'Avg. Outdegree of predecessors', 50)
# dependence(indegree, suc_in_d, '$k_{i}^{suc}(k_i)$', 'indegree', 'Avg. Indegree of successors', 50)
# dependence(indegree, suc_out_d, '$k_{o}^{suc}(k_i)$', 'indegree', 'Avg. Outdegree of successors', 50)

# dependence(outdegree, pre_in_d, '$k_{i}^{pre}(k_o)$', 'outdegree', 'Avg. Indegree of predecessors', 50)
# dependence(outdegree, pre_out_d, '$k_{o}^{pre}(k_o)$', 'outdegree', 'Avg. Outdegree of predecessors', 50)
# dependence(outdegree, suc_in_d, '$k_{i}^{suc}(k_o)$', 'outdegree', 'Avg. Indegree of successors', 50)
# dependence(outdegree, suc_out_d, '$k_{o}^{suc}(k_o)$', 'outdegree', 'Avg. Outdegree of successors', 50)

# dependence(instrength, pre_in_s, '$s_{i}^{pre}(s_i)$', 'Instrength', 'Avg. instrength of predecessors', 50)
# dependence(instrength, pre_out_s, '$s_{o}^{pre}(s_i)$', 'Instrength', 'Avg. outstrength of predecessors', 50)
# dependence(instrength, suc_in_s, '$s_{i}^{suc}(s_i)$', 'Instrength', 'Avg. instrength of successors', 50)
# dependence(instrength, suc_out_s, '$s_{o}^{suc}(s_i)$', 'Instrength', 'Avg. outstrength of successors', 50)

# dependence(outstrength, pre_in_d, '$s_{i}^{pre}(s_o)$', 'Outstrength', 'Avg. instrength of predecessors', 50)
# dependence(outstrength, pre_out_d, '$s_{o}^{pre}(s_o)$', 'Outstrength', 'Avg. outstrength of predecessors', 50)
# dependence(outstrength, suc_in_d, '$s_{i}^{suc}(s_o)$', 'Outstrength', 'Avg. instrength of successors', 50)
# dependence(outstrength, suc_out_d, '$s_{o}^{suc}(s_o)$', 'Outstrength', 'Avg. outstrength of successors', 50)



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