# -*- coding: utf-8 -*-
"""
Created on 10:43 AM, 3/6/16

@author: tw
"""

from sklearn.datasets import load_svmlight_file
from sklearn import preprocessing
from sklearn.svm import SVR, SVC
import pickle
import matplotlib.pyplot as plt
import numpy as np


def regression(train, test, outreg):
    X_train, y_train = load_svmlight_file(train)
    X_train = X_train.toarray()
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    X_test, y_test = load_svmlight_file(test)
    X_test = X_test.toarray()
    X_test = scaler.transform(X_test)
    svr_lin = SVR(kernel='linear')
    y_lin = svr_lin.fit(X_train, y_train).predict(X_test)
    # pickle.dump(y_test, open(outid, 'w'))
    pickle.dump(y_lin, open(outreg, 'w'))
# regression('data/train.data', 'data/test.data', 'data/test_id_reg.pick', 'data/test_reg.pick')


def plot_regression(regres):
    results = pickle.load(open(regres, 'r'))
    print max(results), min(results)
    bins = np.linspace(-3, 4, 100)
    print bins
    print len(results[np.where(results > 4)])
    print len(results[np.where(results < -3)])
    hist, bin_edges = np.histogram(results, bins)
    print sum(hist)
    print len(results[np.where(results > 4)]) + len(results[np.where(results < -3)]) + sum(hist)
    plt.hist(results, bins, histtype='step', cumulative=True)
    plt.title("Regression Results")
    plt.xlabel("Value")
    plt.ylabel("Cumulative Frequency")
    plt.grid(True)
    plt.show()
# plot_regression('data/test_reg.pick')


def classification(train, test, outclss):
    X_train, y_train = load_svmlight_file(train)
    X_train = X_train.toarray()
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    X_test, y_test = load_svmlight_file(test)
    X_test = X_test.toarray()
    X_test = scaler.transform(X_test)
    svc_lin = SVC(kernel='linear')
    y_lin = svc_lin.fit(X_train, y_train).predict(X_test)
    # pickle.dump(y_test, open(outid, 'w'))
    pickle.dump(y_lin, open(outclss, 'w'))


def plot_classification(clares):
    results = pickle.load(open(clares, 'r'))
    print results.shape
    print results
    print max(results), min(results)
    bins = np.linspace(-2, 2, 3)
    print bins
    # print len(results[np.where(results > 1)])
    # print len(results[np.where(results < 0)])
    hist, bin_edges = np.histogram(results, bins)
    print hist, sum(hist)
    # print len(results[np.where(results > 1)]) + len(results[np.where(results < 0)]) + sum(hist)
    plt.hist(results, bins, histtype='bar', rwidth=0.3, alpha=0.5)
    plt.title("Classification Results")
    plt.xlabel("Class")
    plt.ylabel("Frequency")
    plt.xticks([-1, 0, 1], ('Negative', '', 'Positive'))
    plt.grid(True)
    plt.show()


def pclassification(train, test, outpclas):
    X_train, y_train = load_svmlight_file(train)
    X_train = X_train.toarray()
    # y_train[y_train < 0] = 0
    # print y_train
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    X_test, y_test = load_svmlight_file(test)
    X_test = X_test.toarray()
    X_test = scaler.transform(X_test)
    svc_lin = SVC(kernel='linear', probability=True, random_state=0)
    y_lin = svc_lin.fit(X_train, y_train).predict_proba(X_test)
    # pickle.dump(y_test, open(outid, 'w'))
    pickle.dump(y_lin, open(outpclas, 'w'))
# pclassification('data/train.data', 'data/test.data', 'data/test_id_pclass.pick', 'data/test_pclass.pick')


def plot_pclassification(pclares):
    results = pickle.load(open(pclares, 'r'))
    print np.sum(results, axis=1).shape
    results = results[:, 0]/(np.sum(results,axis=1))
    print results.shape
    print results
    print max(results), min(results)
    bins = np.linspace(0, 1, 100)
    print bins
    # print len(results[np.where(results > 1)])
    # print len(results[np.where(results < 0)])
    hist, bin_edges = np.histogram(results, bins)
    print sum(hist)
    # print len(results[np.where(results > 1)]) + len(results[np.where(results < 0)]) + sum(hist)
    plt.hist(results, bins, histtype='bar', rwidth=0.8)
    plt.title("Classification probabilities Results")
    plt.xlabel("Probability")
    plt.ylabel("Frequency")
    # plt.xticks([-1, 0, 1], ('Negative', '', 'Positive'))
    plt.grid(True)
    plt.show()
# plot_pclassification('data/test_pclass.pick')


classification('data/train.data', 'data/test.data',
               'data/test_id_class.pick', 'data/test_class.pick')
plot_classification('data/test_class.pick')