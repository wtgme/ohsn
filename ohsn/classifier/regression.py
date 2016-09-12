# -*- coding: utf-8 -*-
"""
Created on 18:21, 12/09/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.io_util as iot
import matplotlib.pyplot as plt

import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_svmlight_file
from sklearn.linear_model import LassoLarsIC
from sklearn import preprocessing


def regression(train):
    X, y = load_svmlight_file(train)
    X = X.toarray()
    X = preprocessing.scale(X)


    ##############################################################################
    # LassoLarsIC: least angle regression with BIC/AIC criterion

    model_bic = LassoLarsIC(criterion='bic')
    t1 = time.time()
    model_bic.fit(X, y)
    t_bic = time.time() - t1
    alpha_bic_ = model_bic.alpha_

    model_aic = LassoLarsIC(criterion='aic')
    model_aic.fit(X, y)
    alpha_aic_ = model_aic.alpha_

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
    plot_ic_criterion(model_bic, 'BIC', 'r')
    plt.legend()
    plt.title('Information-criterion for model selection (training time %.3fs)'
              % t_bic)
    plt.show()

if __name__ == '__main__':
    regression('data/gbmi.data')