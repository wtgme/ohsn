# -*- coding: utf-8 -*-
"""
Created on 18:25, 06/06/16

@author: wt
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import numpy as np
from scipy import interp
import matplotlib.pyplot as plt
import pandas as pd

from sklearn import metrics
from sklearn import svm, linear_model
from sklearn.metrics import roc_curve, auc
from sklearn.cross_validation import StratifiedKFold
from sklearn.datasets import load_svmlight_file
from sklearn import preprocessing
from sklearn.model_selection import cross_val_predict
import ohsn.util.plot_util as plu
import ohsn.util.io_util as iot
from sklearn import cross_validation
import pickle
import seaborn as sns
from statsmodels.formula.api import logit


def load_scale_data(file_path, multilabeltf=False):
    X, y = load_svmlight_file(file_path, multilabel=multilabeltf)
    X = X.toarray()
    # print X[:, 0]
    # print X[:, 10]
    # print X[:, 21]
    # X = preprocessing.scale(X)
    # min_max_scaler = preprocessing.MinMaxScaler()
    # X = min_max_scaler.fit_transform(X_dentise)
    if multilabeltf == True:
        y = preprocessing.MultiLabelBinarizer().fit_transform(y)
    return (X, y)


def cross_val_roc(X, y):
    print X.shape
    cv = StratifiedKFold(y, n_folds=5)
    classifier = svm.SVC(kernel='linear', class_weight='balanced')
    # classifier = linear_model.LogisticRegression(class_weight='balanced')
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
    print mean_auc
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

def svm_cv(X, y, kernel='linear'):
    # Cross validation with SVM
    clf = svm.SVC(kernel=kernel, class_weight='balanced')
    #When the cv argument is an integer, cross_val_score
    # uses the KFold or StratifiedKFold strategies by default,
    # the latter being used if the estimator derives from ClassifierMixin.
    predicts = cross_val_predict(clf, X, y, cv=5, n_jobs=5)

    acc = metrics.accuracy_score(y, predicts)
    pre = metrics.precision_score(y, predicts, average='weighted')
    rec = metrics.recall_score(y, predicts, average='weighted')
    f1 = metrics.f1_score(y, predicts, average='weighted')

    # scores = cross_validation.cross_val_score(clf, X, y, scoring='accuracy', cv=5, n_jobs=5)
    # print("Accuracy: %0.3f (+/- %0.3f)" % (scores.mean(), scores.std()))
    #
    # scores = cross_validation.cross_val_score(clf, X, y, scoring='precision_weighted', cv=5, n_jobs=5)
    # print("Precision: %0.3f (+/- %0.3f)" % (scores.mean(), scores.std()))
    #
    # scores = cross_validation.cross_val_score(clf, X, y, scoring='recall_weighted', cv=5, n_jobs=5)
    # print("Recall: %0.3f (+/- %0.3f)" % (scores.mean(), scores.std()))
    #
    # scores = cross_validation.cross_val_score(clf, X, y, scoring='f1_weighted', cv=5, n_jobs=5)
    # print("F1: %0.3f (+/- %0.3f)" % (scores.mean(), scores.std()))
    return [acc, pre, rec, f1]

def roc_plot_feature(datafile):
    X, y = load_scale_data(datafile)
    fields = iot.read_fields()
    trim_files = [f.split('.')[-1] for f in fields]
    print len(trim_files)
    select_f = [
        'friend_count', 'status_count', 'follower_count',
        'friends_day', 'statuses_day', 'followers_day',
        'retweet_pro',
        'dmention_pro', 'reply_pro',
        # 'hashtag_pro',
        # 'url_pro',
        'retweet_div',
        'mention_div',
        'reply_div',
        'i', 'we', 'swear', 'negate', 'body', 'health',
        'ingest', 'social', 'posemo', 'negemo']

    indecs = [trim_files.index(f) for f in select_f]
    print indecs
    X = X[:, indecs]
    # '''Calculate positive emotion ratio'''
    # # print X.shape
    # X[:,-2] /= (X[:,-2] + X[:, -1])
    # X = X[:, :-1]
    # X[:, -1][~np.isfinite(X[:, -1])] = 0

    # min_max_scaler = preprocessing.MinMaxScaler()
    # X = min_max_scaler.fit_transform(X)

    X = preprocessing.scale(X)

    print X.shape, y.shape
    # Z = np.append(X, y.reshape((len(y), 1)), axis=1)
    # df = pd.DataFrame(Z, columns=select_f + ['label'])
    # affair_mod = logit("label ~ " + '+'.join(select_f[:-1]), df).fit()
    # print(affair_mod.summary())
    # df.to_csv('scaling-clsuter-feature.csv', index=False)

    print X.shape
    plu.plot_config()
    # ax = plt.gca()
    # ax.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6))

    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 0:12], y)
    # ax.plot(mean_fpr[0:100:5], mean_tpr[0:100:5], 'r--^', label='Soc. (AUC = %0.2f)' % mean_auc, lw=3, ms=10)
    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 12:22], y)
    # ax.plot(mean_fpr[0:100:5], mean_tpr[0:100:5], 'g--d', label='Lin. (AUC = %0.2f)' % mean_auc, lw=3, ms=10)
    #
    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X, y)
    # ax.plot(mean_fpr[0:100:5], mean_tpr[0:100:5], 'b--o', label='All. (AUC = %0.2f)' % mean_auc, lw=3, ms=10)
    # ax.set_xlim([0, 1])
    # ax.set_ylim([0, 1])
    # ax.set_xlabel('False Positive Rate')
    # ax.set_ylabel('True Positive Rate')
    # ax.legend(loc="lower right")
    # ax.grid(True)
    # plt.show()

    data = []
    result = svm_cv(X[:, 0:12], y)
    for i, v in enumerate(result):
        data.append(['Social Activities', i, v])
    result = svm_cv(X[:, 12:22], y)
    for i, v in enumerate(result):
        data.append(['Linguistic Constructs', i, v])
    result = svm_cv(X, y)
    for i, v in enumerate(result):
        data.append(['All', i, v])
    df = pd.DataFrame(data, columns=['Feature', 'Metric', 'Value'])
    plu.plot_config()
    g = sns.factorplot(x="Metric", y="Value", hue="Feature", data=df,
                       kind="bar", legend=False,
                       palette={"Social Activities": "#e9a3c9", "Linguistic Constructs": "#ffffbf", 'All': '#a1d76a'})
    g.set_xticklabels(["Accuracy", "Precision", 'Recall', 'F1'])
    g.set_ylabels('Performance')
    g.set_xlabels('Metric')
    annots = df['Value']
    print annots
    hatches = ['/','/','/','/', '', '','','','\\','\\', '\\','\\']

    ax=g.ax #annotate axis = seaborn axis
    for i, p in enumerate(ax.patches):
        ax.annotate("%.2f" %(annots[i]), (p.get_x() + p.get_width() / 2., p.get_height()),
             ha='center', va='center', fontsize=25, color='black', rotation=0, xytext=(0, 20),
             textcoords='offset points')
        p.set_hatch(hatches[i])
    plt.legend(bbox_to_anchor=(1, 1.2), ncol=6)
    plt.ylim(0.5, 1)
    plt.show()






def roc_plot(datafile, savename, pca_num=10):
    X, y = load_scale_data(datafile)
    print X.shape
    plu.plot_config()
    # plt.rcParams['axes.labelsize'] = 20
    # plt.rcParams['xtick.labelsize'] = 15
    # plt.rcParams['ytick.labelsize'] = 15
    # plt.rcParams['legend.fontsize'] = 20
    # plt.rcParams['lines.markersize'] = 50
    # plt.rcParams['pdf.fonttype'] = 42
    # plt.rcParams['ps.fonttype'] = 42
    ax = plt.gca()
    ax.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6))

    '''social status features'''
    mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 0:6], y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'soc-short.pick', 'w'))
    # mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'soc-short.pick', 'r'))
    ax.plot(mean_fpr[0:100:5], mean_tpr[0:100:5], 'r--^', label='Soc. (AUC = %0.2f)' % mean_auc, lw=3, ms=10)

    '''Behavioral pattern features'''
    mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 6:17], y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'beh.pick', 'w'))
    # mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'beh.pick', 'r'))
    ax.plot(mean_fpr[0:100:5], mean_tpr[0:100:5], 'g--d', label='Beh. (AUC = %0.2f)' % mean_auc, lw=3, ms=10)

    '''LIWC features'''
    mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 17:], y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'liwc.pick', 'w'))
    # mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'liwc.pick', 'r'))
    ax.plot(mean_fpr[0:100:5], mean_tpr[0:100:5], 'b--o', label='Psy. (AUC = %0.2f)' % mean_auc, lw=3, ms=10)

    # '''Plus Hashtag features'''
    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X[:, 21:], y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'liwc-hash.pick', 'w'))
    # mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'liwc-hash.pick', 'r'))
    # ax.plot(mean_fpr[0:100:5], mean_tpr[0:100:5], 'c--o', label='L+H. (area = %0.2f)' % mean_auc, lw=3, ms=10)

    '''All features'''
    '''Remove social impact features'''
    # X_short = np.delete(X, [6,7,8,9], 1)

    mean_fpr, mean_tpr, mean_auc = cross_val_roc(X, y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'all-short.pick', 'w'))
    # mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'all-short.pick', 'r'))
    ax.plot(mean_fpr[0:100:5], mean_tpr[0:100:5], 'k--*', label='All. (AUC = %0.2f)' % mean_auc, lw=3, ms=10)

    '''PCA'''
    # from sklearn import decomposition
    # pca = decomposition.PCA(n_components=pca_num)
    # X = pca.fit_transform(X)
    # mean_fpr, mean_tpr, mean_auc = cross_val_roc(X, y)
    # pickle.dump((mean_fpr, mean_tpr, mean_auc), open(datafile+'red.pick', 'w'))
    # mean_fpr, mean_tpr, mean_auc = pickle.load(open(datafile+'red.pick', 'r'))
    # ax.plot(mean_fpr, mean_tpr, 'c--*', label='Red. (area = %0.2f)' % mean_auc, lw=2, ms=10)

    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.legend(loc="lower right")
    ax.grid(True)
    # plt.gca().set_aspect('equal')
    plt.savefig(savename)
    plt.clf()



if __name__ == '__main__':

    # roc_plot('data/cluster-feature.data', 'pro-ed-recovery.pdf', 90)
    roc_plot_feature('data/cluster-feature.data')
    # roc_plot('data/ed-random.data', 'ed-random-roc.pdf', 90)
    # roc_plot('data/ed-younger.data', 'ed-young-roc.pdf', 70)
    # roc_plot('data/random-younger.data', 'random-young-roc.pdf', 100)

