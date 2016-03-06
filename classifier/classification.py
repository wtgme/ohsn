# -*- coding: utf-8 -*-
"""
Created on 10:43 AM, 3/6/16

@author: tw
"""

from sklearn.datasets import load_svmlight_file
from sklearn import preprocessing
from sklearn.svm import SVR
import pickle


X_train, y_train = load_svmlight_file('data/train.data')
X_train = X_train.toarray()
scaler = preprocessing.StandardScaler().fit(X_train)
X_train = scaler.transform(X_train)

X_test, y_test = load_svmlight_file('data/test.data')
X_test = X_test.toarray()
X_test = scaler.transform(X_test)

svr_lin = SVR(kernel='linear')
y_lin = svr_lin.fit(X_train, y_train).predict(X_test)
pickle.dump(y_test, open('data/test_id.p', 'w'))
pickle.dump(y_lin, open('data/test_reg.p', 'w'))