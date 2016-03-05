# -*- coding: utf-8 -*-
"""
Created on 10:18 PM, 2/27/16

@author: tw
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


def ref(X, y, n_features_to_select=1):
    # specify the desired number of features
    # return the masks and ranking of selected features
    estimator = SVC(kernel="linear")
    selector = RFE(estimator, n_features_to_select=n_features_to_select, step=1)
    selector = selector.fit(X, y)
    return (selector.support_, selector.ranking_)


def rfecv(X, y):
    # recursive feature elimination with SVM
    # CV to find the best set of features

    # Create the RFE object and compute a cross-validated score.
    svc = SVC(kernel="linear")
    # The "accuracy" scoring is proportional to the number of correct
    # classifications
    # Tested: StratifiedKFold works for imbalanced labeled data.
    rfecv = RFECV(estimator=svc, step=1, cv=StratifiedKFold(y, 5),
                  scoring='accuracy')
    rfecv.fit(X, y)

    print("Optimal number of features : %d" % rfecv.n_features_)

    # Plot number of features VS. cross-validation scores
    plt.figure()
    plt.xlabel("Number of features selected")
    plt.ylabel("Cross validation score (nb of correct classifications)")
    plt.plot(range(1, len(rfecv.grid_scores_) + 1), rfecv.grid_scores_)
    plt.grid()
    plt.show()
    # print 'Seleted features', (rfecv.support_)
    # print 'Ranking of features', (rfecv.ranking_)
    # print 'Estimator params', (rfecv.get_params(deep=True))
    return (rfecv.support_, rfecv.ranking_)


def pca_svm_cv(X, y, n=70):
    pca = decomposition.PCA(n_components=n)
    X = pca.fit_transform(X)
    clf = SVC(kernel='linear')
    #When the cv argument is an integer, cross_val_score
    # uses the KFold or StratifiedKFold strategies by default,
    # the latter being used if the estimator derives from ClassifierMixin.
    scores = cross_validation.cross_val_score(clf, X, y, cv=5, scoring='accuracy')
    print("Accuracy: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))


def svm_cv(X, y):
    # Cross validation with SVM
    clf = SVC(kernel='linear')
    #When the cv argument is an integer, cross_val_score
    # uses the KFold or StratifiedKFold strategies by default,
    # the latter being used if the estimator derives from ClassifierMixin.
    scores = cross_validation.cross_val_score(clf, X, y, cv=5, scoring='accuracy')
    print("Accuracy: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))


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


def select_fields(fields, ranks):
    return fields[ranks]


def select_features(X, ranks):
    # select features (columns) according to ranks or binary list
    return X[:, ranks]
    # size = 0
    # for rank in ranks:
    #     if rank == 1:
    #         size += 1
    # row, col = X.shape
    # X_new = np.zeros((row, size))
    # index_new = 0
    # for i in xrange(len(ranks)):
    #     if ranks[i] == 1:
    #         X_new[:, index_new] = X[:, i]
    #         index_new += 1
    # return X_new



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



# pca_svm_cv(X, y)
# supportcv, rankingcv = rfecv(X, y)
# pickle.dump(rankingcv, open("data/rankcv.p", "wb"))
# rankingcv = pickle.load(open("data/rankcv.p", "rb"))
# print rankingcv
# convert_fields(LIWC, rankingcv)

LIWC = read_field()

X1, y1 = load_scale_data('data/ed-nrd-liwc.data')
support1, ranking1 = ref(X1, y1, 38)
convert_fields(LIWC, ranking1)

X2, y2 = load_scale_data('data/ed-nyg-liwc.data')
support2, ranking2 = ref(X2, y2, 31)
convert_fields(LIWC, ranking2)

X3, y3 = load_scale_data('data/ed-all-liwc.data')
support1, ranking1 = rfecv(X1, y1)
support3, ranking3 = ref(X3, y3, 69)
convert_fields(LIWC, ranking3)

comm = np.logical_and(support1, support2)
convert_fields(LIWC, comm)

svm_cv(X1[:, support1], y1)
svm_cv(X2[:, support2], y2)
svm_cv(X3[:, support3], y3)
svm_cv(X1[:, comm], y1)
svm_cv(X2[:, comm], y2)
svm_cv(X3[:, comm], y3)






# X_new = select_features(X, rankingcv)
# LIWC = select_fields(LIWC, rankingcv)
# supportn, rankingn = ref(X_new, y)
# convert_fields(LIWC, rankingn)



# print X.shape
# svm_cv(X, y)
# rank = [1,1,2,31,54,9,47,42,1,1,11,13,8,22,10,36,25,17,37,27,16,45,29,12,41,
#         48,34,24,21,7,1,1,1,1,49,1,35,30,28,51,23,32,6,18,43,19,1,1,1,1,1,
#         1,1,52,1,1,3,39,1,1,1,1,1,1,50,4,33,44,1,14,26,1,1,20,38,5,53,46,40,1,15]
# X_new = select_specific_features(X, rank)
# print X_new.shape
# svm_cv(X_new, y)
#
# rank1 = [0,1,2,31,54,9,47,42,1,1,11,13,8,22,10,36,25,17,37,27,16,45,29,12,41,
#         48,34,24,21,7,1,1,1,1,49,1,35,30,28,51,23,32,6,18,43,19,1,1,1,1,1,
#         1,1,52,1,1,3,39,1,1,1,1,1,1,50,4,33,44,1,14,26,1,1,20,38,5,53,46,40,1,15]
# X_new1 = select_specific_features(X, rank1)
# print X_new1.shape
# svm_cv(X_new1, y)
#
# rank2 = [1,1,2,31,54,9,47,42,0,1,11,13,8,22,10,36,25,17,37,27,16,45,29,12,41,
#         48,34,24,21,7,1,1,1,1,49,1,35,30,28,51,23,32,6,18,43,19,1,1,1,1,1,
#         1,1,52,1,1,3,39,1,1,1,1,1,1,50,4,33,44,1,14,26,1,1,20,38,5,53,46,40,1,15]
# X_new2 = select_specific_features(X, rank2)
# print X_new2.shape
# svm_cv(X_new2, y)

