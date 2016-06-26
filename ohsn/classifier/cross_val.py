# -*- coding: utf-8 -*-
"""
Created on 18:25, 06/06/16

@author: wt
"""
import numpy as np
from scipy import interp
import matplotlib.pyplot as plt

from sklearn import svm
from sklearn.metrics import roc_curve, auc
from sklearn.cross_validation import StratifiedKFold
from sklearn.datasets import load_svmlight_file
from sklearn import preprocessing
import pickle


def load_scale_data(file_path, multilabeltf=False):
    X, y = load_svmlight_file(file_path, multilabel=multilabeltf)
    X = X.toarray()
    # print X[:, 0]
    # print X[:, 10]
    # print X[:, 21]
    X = preprocessing.scale(X)
    # min_max_scaler = preprocessing.MinMaxScaler()
    # X = min_max_scaler.fit_transform(X_dentise)
    if multilabeltf == True:
        y = preprocessing.MultiLabelBinarizer().fit_transform(y)
    return (X, y)


def cross_val_roc(X, y):
    cv = StratifiedKFold(y, n_folds=5)
    classifier = svm.SVC(kernel='linear', class_weight='balanced')
    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    for i, (train, test) in enumerate(cv):
        predict = classifier.fit(X[train], y[train]).predict(X[test])
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(y[test], predict)
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
    mean_tpr /= len(cv)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    # plt.plot(mean_fpr, mean_tpr, color+'--',
    #          label=feature+' (area = %0.2f)' % mean_auc, lw=2)
    return mean_fpr, mean_tpr, mean_auc



def cross_val_roc_plot(X, y):
    cv = StratifiedKFold(y, n_folds=5)
    classifier = svm.SVC(kernel='linear', class_weight='balanced')
    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    all_tpr = []
    for i, (train, test) in enumerate(cv):
        predict = classifier.fit(X[train], y[train]).predict(X[test])
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(y[test], predict)
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
    mean_tpr /= len(cv)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    plt.plot(mean_fpr, mean_tpr, 'k--',
             label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)

    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()


def roc_plot(datafile, savename):
    X, y = load_scale_data(datafile)

    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['legend.fontsize'] = 20
    ax = plt.gca()
    ax.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6))

    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 0:9], y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'soc.pick', 'w'))
    mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'soc.pick', 'r'))
    ax.plot(mean_fpr, mean_tpr, 'r--^', label='Soc. (area = %0.2f)' % mean_auc, lw=2, ms=10)

    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 10:20], y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'beh.pick', 'w'))
    mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'beh.pick', 'r'))
    ax.plot(mean_fpr, mean_tpr, 'g--+', label='Beh. (area = %0.2f)' % mean_auc, lw=2, ms=10)

    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 21:], y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'liwc.pick', 'w'))
    mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'liwc.pick', 'r'))
    ax.plot(mean_fpr, mean_tpr, 'b--.', label='Psy. (area = %0.2f)' % mean_auc, lw=2, ms=10)

    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X, y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'all.pick', 'w'))
    mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'all.pick', 'r'))
    ax.plot(mean_fpr, mean_tpr, 'k--*', label='All. (area = %0.2f)' % mean_auc, lw=2, ms=10)

    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.legend(loc="lower right")
    ax.grid(True)
    plt.savefig(savename)
    plt.clf()

if __name__ == '__main__':
    roc_plot('data/ed-random.data', 'ed-random-roc.pdf')
    roc_plot('data/ed-young.data', 'ed-young-roc.pdf')
    roc_plot('data/random-young.data', 'random-young-roc.pdf')


