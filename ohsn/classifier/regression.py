# -*- coding: utf-8 -*-
"""
Created on 18:21, 12/09/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.io_util as iot
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_svmlight_file
from sklearn.linear_model import LassoLarsIC, LassoCV
from sklearn import preprocessing
import seaborn as sns


def read_data(train):
    X, y = load_svmlight_file(train)
    print X.shape, y.shape
    xmax = np.percentile(y, 97.5)
    xmin = np.percentile(y, 2.5)
    """Plot GBMI(y) distribution"""
    sns.distplot(y)
    plt.axvline(xmin, linestyle='--', color='k',
                    label='Min 2.5% Cut-off')
    plt.axvline(xmax, linestyle='--', color='k',
                    label='Max 2.5% Cut-off')
    plt.legend()
    plt.xlabel('GBMI')
    plt.ylabel('PDF')
    plt.show()
    indeces = np.logical_and(y>=xmin, y<=xmax)

    y = y[indeces]
    X = X[indeces].toarray()
    X = preprocessing.scale(X)
    print X.shape, y.shape
    return X, y

def parameter_select(X, y):
    print X.shape, y.shape
    ##############################################################################
    # LassoLarsIC: least angle regression with BIC/AIC criterion
    # model_bic = LassoLarsIC(criterion='bic')
    # model_bic.fit(X, y)
    # alpha_bic_ = model_bic.alpha_
    model_aic = LassoLarsIC(criterion='aic', max_iter=100000000)
    model_aic.fit(X, y)
    alpha_aic_ = model_aic.alpha_
    print alpha_aic_

    def plot_ic_criterion(model, name, color):
        alpha_ = model.alpha_
        alphas_ = model.alphas_
        criterion_ = model.criterion_
        plt.plot(-np.log10(alphas_), criterion_, '--', color=color,
                 linewidth=3, label='%s criterion' % name)
        plt.axvline(-np.log10(alpha_), color=color, linewidth=3,
                    label='alpha: %s estimate' % name)
        plt.xlabel('-log(alpha)')
        plt.ylabel('criterion')

    plt.figure()
    plot_ic_criterion(model_aic, 'AIC', 'b')
    # plot_ic_criterion(model_bic, 'BIC', 'r')
    plt.legend()
    plt.title('Information-criterion for model selection')
    plt.show()

    fields = iot.read_fields()
    for i in xrange(len(fields)):
        print str(fields[i]) +'\t'+ str(model_aic.coef_[i])


def msepath(X, y):
    print X.shape, y.shape
    # Compute paths
    print("Computing regularization path using the coordinate descent lasso...")
    model = LassoCV(cv=10, max_iter=3000).fit(X, y)

    # Display results
    m_log_alphas = -np.log10(model.alphas_)

    plt.figure()
    plt.plot(m_log_alphas, model.mse_path_, ':')
    plt.plot(m_log_alphas, model.mse_path_.mean(axis=-1), 'k',
             label='Average across the folds', linewidth=2)
    plt.axvline(-np.log10(model.alpha_), linestyle='--', color='k',
                label='alpha: CV estimate')

    plt.legend()
    plt.xlabel('-log(alpha)')
    plt.ylabel('Mean square error')
    plt.title('Mean square error on each fold: coordinate descent')
    plt.axis('tight')
    plt.show()

    fields = iot.read_fields()
    for i in xrange(len(fields)):
        print str(fields[i]) +'\t'+ str(model.coef_[i])


if __name__ == '__main__':
    X, y = read_data('data/gbmi.data')
    parameter_select(X, y)
    print '---------------------------------'
    msepath(X, y)