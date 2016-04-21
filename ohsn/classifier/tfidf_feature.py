# -*- coding: utf-8 -*-
"""
Created on 10:45 PM, 4/5/16

@author: tw
"""

from sklearn.datasets import load_files
from pprint import pprint
from sklearn.svm import LinearSVC, SVC
from sklearn import cross_validation
from sklearn.feature_extraction.text import TfidfVectorizer

def svm_cv(filepath):
    corpus = load_files(filepath)
    pprint(list(corpus.target_names))
    vectorizer = TfidfVectorizer(max_df=0.95, min_df=5)
    X = vectorizer.fit_transform(corpus.data)
    y = corpus.target
    print y.shape
    print y
    print X.shape

    clf = SVC(kernel='linear')
    scores = cross_validation.cross_val_score(clf, X, y, scoring='accuracy', cv=5, n_jobs=5)
    print("Accuracy: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))

svm_cv('data/word')
svm_cv('data/tag')

