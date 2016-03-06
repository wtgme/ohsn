# -*- coding: utf-8 -*-
"""
Created on 10:18 PM, 2/27/16

@author: tw

Tested:
1. linear svm is better than others
2. balanced setting is colse to non-balanced setting, but with more features. So using Non-balanced setting.
3. SVC probabilities or SVR: the cross-validation involved in Platt scaling is an expensive operation for
large datasets. In addition, the probability estimates may be inconsistent with the scores, in the sense that
the “argmax” of the scores may not be the argmax of the probabilities. (E.g., in binary classification,
a sample may be labeled by predict as belonging to a class that has probability <½ according to predict_proba.)
Platt’s method is also known to have theoretical issues. So using SVR.
"""

import matplotlib.pyplot as plt

import numpy as np
from sklearn.datasets import load_svmlight_file
from sklearn import decomposition
from sklearn import cross_validation
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn import preprocessing
from sklearn.svm import LinearSVC, SVC
from sklearn.cross_validation import StratifiedKFold
from sklearn.feature_selection import RFECV, RFE, SelectFromModel
import pickle


def read_field():
    # read feature names in use
    fileds = []
    with open('fieldx.txt', 'r') as fo:
        for line in fo.readlines():
            fileds.append(line.strip().split('.')[-1])
    return np.array(fileds)


def pac_svc(X_digits, y_digits):
    # PCA and SVM test best number of components
    svc = SVC(kernel="linear")

    pca = decomposition.PCA()
    pipe = Pipeline(steps=[('pca', pca), ('svc', svc)])

    ###############################################################################
    # Plot the PCA spectrum
    pca.fit(X_digits)

    plt.figure(1)
    plt.clf()
    # plt.axes([.2, .2, .7, .7])
    plt.plot(pca.explained_variance_, linewidth=2)
    plt.axis('tight')
    plt.xlabel('n_components')
    plt.ylabel('explained_variance_')
    print pca.explained_variance_ratio_
    print pca.explained_variance_

    ###############################################################################
    # Prediction

    n_components = [10, 20, 30, 40, 50, 60, 70, 80]

    #Parameters of pipelines can be set using ‘__’ separated parameter names:

    estimator = GridSearchCV(pipe,
                             dict(pca__n_components=n_components))
    estimator.fit(X_digits, y_digits)

    plt.axvline(estimator.best_estimator_.named_steps['pca'].n_components,
                linestyle=':', label='n_components chosen')
    plt.legend(prop=dict(size=12))
    plt.show()


def ref(X, y, n_features_to_select=1, kernel='linear'):
    # specify the desired number of features
    # return the masks and ranking of selected features
    estimator = SVC(kernel=kernel)
    selector = RFE(estimator, n_features_to_select=n_features_to_select, step=1)
    selector = selector.fit(X, y)
    return (selector)


def rfecv(X, y, kernel='linear', class_weight=None):
    # RFECV currently only support linear models with a coef_ attribute.
    # It should probably be possible generalized to use the feature_importances_
    # recursive feature elimination with SVM
    # CV to find the best set of features
    # Create the RFE object and compute a cross-validated score.
    svc = SVC(kernel=kernel, class_weight=class_weight)
    # The "accuracy" scoring is proportional to the number of correct
    # classifications
    # Tested: StratifiedKFold works for imbalanced labeled data.
    rfecv = RFECV(estimator=svc, step=1, cv=StratifiedKFold(y, 5),
                  scoring='accuracy')
    rfecv.fit(X, y)
    print("Optimal number of features : %d" % rfecv.n_features_)
    return (rfecv)


def plot_rfecvs(rfecvs, labels):
    # Plot number of features VS. cross-validation scores
    plt.figure()
    # marks = ['*', '^', 'o']
    plt.xlabel("Number of features selected")
    plt.ylabel("Cross validation score (nb of correct classifications)")
    for i in xrange(len(rfecvs)):
        plt.plot(range(1, len(rfecvs[i]) + 1), rfecvs[i], label=labels[i])
    plt.legend(loc="best")
    plt.grid()
    plt.show()


def plot_errorbar(score_means, score_stds, labels):
    plt.figure()
    # plt.xlabel("Number of features selected")
    plt.ylabel("Cross validation performance")
    for i in xrange(len(score_means)):
        plt.errorbar(i+1, score_means[i], np.array(score_stds[i]), fmt="o", label=labels[i])
    plt.xticks(range(len(score_means)+2))
    plt.ylim(0.4, 1)
    plt.legend()
    plt.grid()
    plt.show()


def pca_svm_cv(X, y, n=70):
    pca = decomposition.PCA(n_components=n)
    X = pca.fit_transform(X)
    clf = SVC(kernel='linear')
    #When the cv argument is an integer, cross_val_score
    # uses the KFold or StratifiedKFold strategies by default,
    # the latter being used if the estimator derives from ClassifierMixin.
    scores = cross_validation.cross_val_score(clf, X, y, scoring='accuracy', cv=5, n_jobs=5)
    print("Accuracy: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))


def svm_cv(X, y, kernel='linear'):
    # Cross validation with SVM
    clf = SVC(kernel=kernel)
    #When the cv argument is an integer, cross_val_score
    # uses the KFold or StratifiedKFold strategies by default,
    # the latter being used if the estimator derives from ClassifierMixin.
    scores = cross_validation.cross_val_score(clf, X, y, scoring='accuracy', cv=5, n_jobs=5)
    print("Accuracy: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
    return scores


def fs_svm(X, y):
    # feature selection with SVM model
    lsvc = LinearSVC(C=0.001, penalty="l1", dual=False).fit(X, y)
    model = SelectFromModel(lsvc, prefit=True)
    X_new = model.transform(X)

    LIWC = read_field()
    print 'Original feature size', X.shape
    print 'New feature size', X_new.shape
    sample_X = X[0]
    sample_X_new = X_new[0]
    print 'Original feature length of sample', len(set(sample_X))
    print 'New feature length of sample', len(set(sample_X_new))
    for i in xrange(len(sample_X)):
        if sample_X[i] in sample_X_new:
            print i+1, LIWC[i]


def convert_fields(LIWC, rank):
    # Convert ranking IDs to feature names and rank them
    rf = {}
    for i in xrange(len(rank)):
        key = rank[i]
        field = LIWC[i]
        flist = rf.get(key, [])
        flist.append(field)
        rf[key] = flist
    # output
    line_tag = ''
    line_non_tag = ''
    for key in sorted(rf):
        flist = rf[key]
        line = ''
        for f in flist:
            line += f + '; '
        if key == 1:
            line_tag += line
        else:
            line_non_tag += line

    print 'Selected Features:, ', line_tag
    print 'Eliminated Features:, ', line_non_tag


def load_scale_data(file_path):
    X_digits, y = load_svmlight_file(file_path)
    X_dentise = X_digits.toarray()
    X = preprocessing.scale(X_dentise)
    # min_max_scaler = preprocessing.MinMaxScaler()
    # X = min_max_scaler.fit_transform(X_dentise)
    return (X, y)


def common_features():
    LIWC = read_field()
    X1, y1 = load_scale_data('data/ed-nrd-liwc.data')
    ref1 = ref(X1, y1, 38)
    support1, ranking1 = ref1.support_, ref1.ranking_
    convert_fields(LIWC, ranking1)
    X2, y2 = load_scale_data('data/ed-nyg-liwc.data')
    ref2 = ref(X2, y2, 31)
    support2, ranking2 = ref2.support_, ref2.ranking_
    convert_fields(LIWC, ranking2)
    # X3, y3 = load_scale_data('data/ed-all-liwc.data')
    # ref3 = ref(X3, y3, 69)
    # support3, ranking3 = ref3.support_, ref3.ranking_
    # convert_fields(LIWC, ranking3)

    comm = np.logical_and(support1, support2)
    convert_fields(LIWC, comm)
    pickle.dump(comm, open('data/common.p', 'wb'))
    # svm_cv(X1[:, support1], y1)
    # svm_cv(X2[:, support2], y2)
    # svm_cv(X3[:, support3], y3)
    # svm_cv(X1[:, comm], y1)
    # svm_cv(X2[:, comm], y2)
    # svm_cv(X3[:, comm], y3)


def kernels():
    X1, y1 = load_scale_data('data/ed-nrd-liwc.data')
    ref1 = ref(X1, y1, 38)
    support1, ranking1 = ref1.support_, ref1.ranking_
    labels = ['linear', 'poly', 'rbf', 'sigmoid']
    means, stds = list(), list()
    for label in labels:
        score = svm_cv(X1[:, support1], y1, kernel=label)
        means.append(score.mean())
        stds.append(score.std())
    plot_errorbar(means, np.array(stds), labels)


def balanced():
    X1, y1 = load_scale_data('data/ed-all-liwc.data')
    # # ref1 = ref(X1, y1, 38)
    # # pickle.dump(ref1, open('data/ref.p', 'wb'))
    # ref1 = pickle.load(open('data/ref.p', 'rb'))
    # rfecv1 = rfecv(X1, y1)
    # rfecv2 = rfecv(X1, y1, class_weight='balanced')
    rfecv1 = pickle.load(open('data/rfecv1.p', 'rb'))
    rfecv2 = pickle.load(open('data/rfecv2.p', 'rb'))
    scores = list()
    scores.append(rfecv1.grid_scores_)
    scores.append(rfecv2.grid_scores_)
    plot_rfecvs(scores, ['Non-balanced', 'Balanced'])


common_features()

