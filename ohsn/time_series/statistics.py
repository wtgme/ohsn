# -*- coding: utf-8 -*-
"""
Created on 11:44 AM, 5/27/16

@author: tw

Conduct descriptive statistics on time series data
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.plot_util as plot
import ohsn.util.statis_util as stt
import ohsn.util.io_util as iot
import numpy as np
import matplotlib.pyplot as plt


def central_values(lista):
    maxv = np.percentile(lista, 97.5)
    minv = np.percentile(lista, 2.5)
    return [x for x in lista if minv<=x<=maxv]


def avg_liwc(dbname):
    fields = iot.read_fields()
    for field in fields:
        filters = {field: {'$exists': True}}
        results = list()
        N = 5
        for i in range(1, N+1):
            result = iot.get_values_one_field(dbname, dbname+'com_t'+str(i), field, filters)
            result = central_values(result)
            results.append(result)
        ax = plt.gca()
        ind = [y+1 for y in range(len(results))]
        means = [np.mean(result) for result in results]
        stds = [np.std(result) for result in results]
        ax.errorbar(ind, means, fmt='--o--', capthick=3)
        ax.violinplot(results, showmeans=False, showextrema=True)
        ax.set_xticks(ind)
        # for i in ind:
        #     ax.text(i, means[i-1]+0.5,
        #         str(round(means[i-1], 2))+ '$\pm$'+ str(round(stds[i-1], 2)),
        #         ha='center', va='bottom', )
        ax.set_xticklabels(('Before 2012', '2012', '2013', '2014', 'After 2014'))
        ax.set_xlabel('Time Series')
        tokens = field.split('.')
        if tokens[-1] == 'value':
            ax.set_ylabel(tokens[-2].upper())
        else:
            ax.set_ylabel(tokens[-1])
        ax.grid(True)
        plt.savefig(field+'.pdf')
        plt.clf()


if __name__ == '__main__':
    avg_liwc('fed')