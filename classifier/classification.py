# -*- coding: utf-8 -*-
"""
Created on 10:18 PM, 2/27/16

@author: tw
"""

import matplotlib.pyplot as plt

from sklearn.datasets import load_svmlight_file
from sklearn import linear_model, decomposition
from sklearn import cross_validation
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn import preprocessing
from sklearn.svm import LinearSVC, SVC
from sklearn.feature_selection import SelectFromModel
from sklearn.cross_validation import StratifiedKFold
from sklearn.feature_selection import RFECV


def read_field():
    fileds = []
    with open('fieldx.txt', 'r') as fo:
        for line in fo.readlines():
            fileds.append(line.strip().split('.')[-1])
    return fileds


def pac_svc(X_digits, y_digits):
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


def convert_fields(rank):
    LIWC = read_field()
    rf = {}
    for i in xrange(len(rank)):
        key = rank[i]
        field = LIWC[i]
        flist = rf.get(key, [])
        flist.append(field)
        rf[key] = flist
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


def rfe(X, y):
    # Create the RFE object and compute a cross-validated score.
    svc = SVC(kernel="linear")
    # The "accuracy" scoring is proportional to the number of correct
    # classifications
    rfecv = RFECV(estimator=svc, step=1, cv=StratifiedKFold(y, 5),
                  scoring='accuracy')
    rfecv.fit(X, y)

    print("Optimal number of features : %d" % rfecv.n_features_)

    # Plot number of features VS. cross-validation scores
    plt.figure()
    plt.xlabel("Number of features selected")
    plt.ylabel("Cross validation score (nb of correct classifications)")
    plt.plot(range(1, len(rfecv.grid_scores_) + 1), rfecv.grid_scores_)
    plt.show()
    print 'Seleted features', (rfecv.support_)
    print 'Ranking of features', (rfecv.ranking_)
    return (rfecv.support_, rfecv.ranking_)


def svm_cv(X, y):
    clf = SVC(kernel='linear')
    scores = cross_validation.cross_val_score(clf, X, y, cv=5)
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


def fs_svm(X, y):
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


X_digits, y_digits = load_svmlight_file("data/ed-rd-liwc.data")
X_dentise = X_digits.toarray()

X = preprocessing.scale(X_dentise)
# min_max_scaler = preprocessing.MinMaxScaler()
# X = min_max_scaler.fit_transform(X_dentise)

# fs_svm(X, y_digits)


# rfe(X, y_digits)
rank = [1,1,2,31,54,9,47,42,1,1,11,13,8,22,10,36,25,17,37,27,16,45,29,12,41,
        48,34,24,21,7,1,1,1,1,49,1,35,30,28,51,23,32,6,18,43,19,1,1,1,1,1,
        1,1,52,1,1,3,39,1,1,1,1,1,1,50,4,33,44,1,14,26,1,1,20,38,5,53,46,40,1,15]
convert_fields(rank)