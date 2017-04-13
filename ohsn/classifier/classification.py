# -*- coding: utf-8 -*-
"""
Created on 10:43 AM, 3/6/16

@author: tw
"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
from sklearn.datasets import load_svmlight_file
from sklearn import preprocessing
import ohsn.util.io_util as iot
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
    print X_train.shape
    print X_test.shape
    # for xi in X_test.T:
    #     print min(xi), max(xi)
    X_test = scaler.transform(X_test)

    svc_lin = SVC(kernel='linear', class_weight='balanced')
    y_lin = svc_lin.fit(X_train, y_train).predict(X_test)
    # pickle.dump(y_test, open(outid, 'w'))
    pickle.dump(y_lin, open(outclss, 'w'))
    '''Int to numpy.int will lost precision'''
    # pickle.dump(y_test[y_lin==1], open('result.pick', 'w'))
    # print y_test[y_lin==1].astype('str')
    return y_lin


def classification_subfeature(train, test, outclss):
    fields = iot.read_fields()
    print len(fields)
    foi = ['liwc_anal.result.i',
           'liwc_anal.result.we',
           'liwc_anal.result.affect',
           'liwc_anal.result.posemo',
           'liwc_anal.result.negemo',
           'liwc_anal.result.bio',
           'liwc_anal.result.body',
           'liwc_anal.result.health',
           'liwc_anal.result.ingest']
    indeces = [np.where(fields==f)[0][0] for f in foi]
    print fields[indeces]

    '''Load Training data'''
    X_train, y_train = load_svmlight_file(train)
    X_train = X_train.toarray()[:, indeces]
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    print X_train.shape
    '''Load Test data'''
    X_test, y_test = load_svmlight_file(test)
    X_test = X_test.toarray()[:, indeces]
    X_test = scaler.transform(X_test)
    print X_test.shape

    svc_lin = SVC(kernel='linear', class_weight='balanced')
    y_lin = svc_lin.fit(X_train, y_train).predict(X_test)
    # pickle.dump(y_test, open(outid, 'w'))
    pickle.dump(y_lin, open(outclss, 'w'))




def plot_classification(results):
    # Plot classification results
    print results.shape
    print results
    print max(results), min(results)
    bins = np.linspace(-2, 2, 3)
    print bins
    print len(results[np.where(results == 1)])
    print len(results[np.where(results == 0)])
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
    # Probability classification, return probability
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


def predict_verify(dbname, comname, testname, lables):
    ids = pickle.load(open(testname+'_ids.data', 'r'))
    print len(ids), len(lables)
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    pred_users = []
    # +1 for ED and -1 for non-ED
    for i in xrange(len(ids)):
        if lables[i] == 1:
            pred_users.append(ids[i])

    for uid in pred_users:
        user = com.find_one({'id': int(uid)})
        if user['level'] != 1:
            print user['screen_name'].encode('utf-8')
        # print uid, user['screen_name'].encode('utf-8'), ' '.join(user['description'].split()).encode('utf-8')


def compare_round(dbname, comname, testname, lables1, labels2):
    ids = pickle.load(open(testname+'_ids.data', 'r'))
    print len(ids), len(lables1), len(labels2)
    db = dbt.db_connect_no_auth(dbname)
    com = db[comname]
    pred_users = []
    # +1 for ED and -1 for non-ED
    for i in xrange(len(ids)):
        if lables1[i] == 1 and labels2[i] == -1:
            pred_users.append(ids[i])
    for uid in pred_users:
        user = com.find_one({'id': int(uid)})
        if user['level'] != 1:
            # print user['screen_name'].encode('utf-8')
            print uid, user['screen_name'].encode('utf-8'), ' '.join(user['description'].split()).encode('utf-8')

def classification_round(X_train, X_test, y_train):
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)
    print 'X_traing size:', X_train.shape
    print 'X_test size:', X_test.shape
    svc_lin = SVC(kernel='linear', class_weight='balanced')
    y_lin = svc_lin.fit(X_train, y_train).predict(X_test)
    return y_lin


def ite_classification(train, test):
    # First use random and ED users to predict ED and non-ED users
    # Then, use ED and predicted non-ED users to predict ED and non-ED users
    # X_train, y_train = load_svmlight_file(train)
    # X_train = X_train.toarray()
    # X_test, y_test = load_svmlight_file(test)
    # X_test = X_test.toarray()
    # First round classification
    # y_pre_1 = classification_round(X_train, X_test, y_train)
    # pickle.dump(y_pre_1, open('data/one-prediction', 'w'))
    y_pre = pickle.load(open('data/prediction-'+str(1), 'r'))
    # predict_verify('fed', 'com', 'data/fed', y_pre_1)
    print 'Negative samples:', len(y_pre[y_pre == -1])
    print 'Positive samples:', len(y_pre[y_pre == 1])

    # Second round classification
    for i in xrange(2, 10):
        print 'Classification-round', i
        # X_train = X_train[y_train==1]
        # y_train = np.ones(len(X_train))
        # neg_predict = X_test[y_pre == -1]
        # X_train = np.vstack((X_train, neg_predict))
        # neg_y = np.negative(np.ones(len(neg_predict)))
        # y_train = np.append(y_train, neg_y)
        # y_pre = classification_round(X_train, X_test, y_train)
        # pickle.dump(y_pre, open('data/prediction-'+str(i), 'w'))
        y_pre = pickle.load(open('data/prediction-'+str(i), 'r'))
        print 'Negative samples:', len(y_pre[y_pre == -1])
        print 'Positive samples:', len(y_pre[y_pre == 1])
    # y_pre_2 = pickle.load(open('data/prediction-'+str(2), 'r'))
    # predict_verify('fed', 'com', 'data/fed', y_pre_2)


def out_predicted_users_ids(results, test_file):
    # output the users ids that have been predicted as positive
    ids = []
    with open(test_file, 'r') as fo:
        i = 0
        for line in fo.readlines():
            id = line.strip().split()[0]
            if results[i] == 1:
                ids.append(id)
            i += 1
    print len(ids)
    pickle.dump(ids, open('data/positive.pick', 'w'))


if __name__ == '__main__':
    '''classification with all features'''
    # classification('data/ed-noned.data', 'data/fed.data',
    #                'data/fed.pick')
    results = pickle.load(open('data/fed.pick', 'r'))
    # plot_classification(results)
    out_predicted_users_ids(results, 'data/fed.data')
    # predict_verify('fed', 'com', 'data/fed', results)


    # """Refine results with subset of features"""
    # # classification_subfeature('data/ed-random.data', 'data/ed-tria.data',
    # #                           'data/subfeature_test_id_class.pick')
    # results2 = pickle.load(open('data/subfeature_test_id_class.pick', 'r'))
    # print results2
    #
    # """combine the results that are obtained with All features and subset of features"""
    # common = []
    # for i in xrange(len(results)):
    #     if results[i]==1 and results2[i]==1:
    #         common.append(+1)
    #     else:
    #         common.append(-1)
    # common = np.array(common)
    # print common.shape, results.shape, results2.shape
    # # plot_classification(common)
    #
    # """verify results"""
    # predict_verify('fed', 'com', 'data/ed-tria', common)



    # ite_classification('data/ed-rd.data', 'data/fed.data')
    # y_pre1 = pickle.load(open('data/prediction-'+str(2), 'r'))
    # y_pre2 = pickle.load(open('data/prediction-'+str(3), 'r'))
    # compare_round('fed', 'com', 'data/fed', y_pre1, y_pre2)
