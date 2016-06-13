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
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.io_util as iot
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
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import pickle
import itertools
from sklearn.metrics import f1_score



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
    estimator = SVC(kernel=kernel, class_weight='balanced')
    selector = RFE(estimator, n_features_to_select=n_features_to_select, step=1)
    selector = selector.fit(X, y)
    return (selector)


def rfecv(X, y, kernel='linear'):
    # RFECV currently only support linear models with a coef_ attribute.
    # It should probably be possible generalized to use the feature_importances_
    # recursive feature elimination with SVM
    # CV to find the best set of features
    # Create the RFE object and compute a cross-validated score.
    svc = SVC(kernel=kernel, class_weight='balanced')
    # The "accuracy" scoring is proportional to the number of correct
    # classifications
    # Tested: StratifiedKFold works for imbalanced labeled data.
    rfecv = RFECV(estimator=svc, step=1, cv=StratifiedKFold(y, 5),
                  scoring='accuracy')
    rfecv.fit(X, y)
    print("Optimal number of features : %d" % rfecv.n_features_)
    return (rfecv)


def mlrfecv(X, y, kernel='linear', class_weight=None):
    classif = OneVsRestClassifier(SVC(kernel=kernel, class_weight=class_weight))
    mrfecv = RFECV(estimator =classif, step=1, cv=StratifiedKFold(y, 5),
                  scoring='f1_samples')
    rfecv.fit(X, y)
    print("Optimal number of features : %d" % mrfecv.n_features_)
    return (mrfecv)


def plot_rfecvs(rfecvs, labels):
    # Plot number of features VS. cross-validation scores
    plt.figure()
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['legend.fontsize'] = 20
    marker = itertools.cycle((',', '+', '.', 'o', '*'))
    plt.xlabel("#Features")
    plt.ylabel("Cross validation AUC")
    for i in xrange(len(rfecvs)):
        rfecv = rfecvs[i]
        label = labels[i]
        c = np.random.rand(3)

        plt.plot(range(1, len(rfecv.grid_scores_) + 1), rfecv.grid_scores_,
                 label=label,
                 c=c, marker=marker.next(), lw=2
                 )
        plt.axvline(rfecv.n_features_, linestyle='dashdot', c=c, lw=2)
        plt.annotate('Best: (' + str(rfecv.n_features_) + ', ' + str(round(rfecv.grid_scores_[rfecv.n_features_-1]*100, 2))+'%)',
                 xy=(rfecv.n_features_, rfecv.grid_scores_[rfecv.n_features_-1]),  xycoords='data',
                 xytext=(-30, -30*(i+1)), textcoords='offset points', fontsize=20,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
        # plt.annotate(str(rfecv.n_features_)+', '+str(rfecv.grid_scores_[rfecv.n_features_-1]),
        #              xy=(rfecv.n_features_, rfecv.grid_scores_[rfecv.n_features_-1]),
        #              xytext=(rfecv.n_features_, rfecv.grid_scores_[rfecv.n_features_-1]-0.2)
        #              )
    plt.legend(loc="best")
    plt.grid()
    plt.show()
    plt.savefig('refcv.pdf')
    plt.clf()



def plot_errorbar(score_means, score_stds, labels):
    plt.figure()
    # plt.xlabel("Number of features selected")
    index = np.arange(len(score_means))
    bar_width = 0.5
    opacity = 0.4
    error_config = {'ecolor': '0.3'}
    plt.ylabel("Cross validation performance")
    # for i in xrange(len(score_means)):
    #     plt.errorbar(i+1, score_means[i], np.array(score_stds[i]), fmt="o", label=labels[i])
    plt.bar(index, score_means, bar_width, alpha=opacity, color='b',
                 yerr=score_stds, error_kw=error_config, label='Accuracy')
    plt.xticks(index + bar_width/2, labels)
    # plt.xticks(range(len(score_means)), labels)
    plt.ylim(0.45, 1)
    # plt.xlim(-1, len(score_means))
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


def mlsvm_cv(X, y, kernel='linear'):
    # Cross validation with SVM
    print 'Multiple label classification'
    classif = OneVsRestClassifier(SVC(kernel=kernel))
    #When the cv argument is an integer, cross_val_score
    # uses the KFold or StratifiedKFold strategies by default,
    # the latter being used if the estimator derives from ClassifierMixin.
    scores = cross_validation.cross_val_score(classif, X, y, scoring='f1_samples', cv=5, n_jobs=5)
    print("F1_samples: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
    return scores


def svm_cv(X, y, kernel='linear'):
    # Cross validation with SVM
    clf = SVC(kernel=kernel, class_weight='balanced')
    #When the cv argument is an integer, cross_val_score
    # uses the KFold or StratifiedKFold strategies by default,
    # the latter being used if the estimator derives from ClassifierMixin.
    scores = cross_validation.cross_val_score(clf, X, y, scoring='accuracy', cv=5, n_jobs=5)
    print("Accuracy: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std()))

    scores = cross_validation.cross_val_score(clf, X, y, scoring='precision_weighted', cv=5, n_jobs=5)
    print("Precision: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std()))

    scores = cross_validation.cross_val_score(clf, X, y, scoring='recall_weighted', cv=5, n_jobs=5)
    print("Recall: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std()))

    scores = cross_validation.cross_val_score(clf, X, y, scoring='f1_weighted', cv=5, n_jobs=5)
    print("F1: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std()))

    # scores = cross_validation.cross_val_score(clf, X, y, scoring='roc_auc_weighted', cv=5, n_jobs=5)
    # print("AUC: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std()))

    return scores


def fs_svm(X, y):
    # feature selection with SVM model
    lsvc = LinearSVC(C=0.001, penalty="l1", dual=False).fit(X, y)
    model = SelectFromModel(lsvc, prefit=True)
    X_new = model.transform(X)

    LIWC = iot.read_fields()
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


def load_scale_data(file_path, multilabeltf=False):
    X, y = load_svmlight_file(file_path, multilabel=multilabeltf)
    X = X.toarray()
    X = preprocessing.scale(X)
    # min_max_scaler = preprocessing.MinMaxScaler()
    # X = min_max_scaler.fit_transform(X_dentise)
    if multilabeltf == True:
        y = MultiLabelBinarizer().fit_transform(y)
    return (X, y)


def common_features():
    '''Need no scoring metrics'''
    LIWC = iot.read_fields()
    LIWC = [line.strip().split('.')[-1] for line in LIWC]
    X1, y1 = load_scale_data('data/ed-random.data')
    X2, y2 = load_scale_data('data/ed-young.data')

    '''Feature rankings'''
    ref1 = ref(X1, y1)
    support1, ranking1 = ref1.support_, ref1.ranking_
    convert_fields(LIWC, ranking1)

    ref2 = ref(X2, y2)
    support2, ranking2 = ref2.support_, ref2.ranking_
    convert_fields(LIWC, ranking2)
    # # X3, y3 = load_scale_data('data/ed-all-liwc.data')
    # # ref3 = ref(X3, y3, 69)
    # # support3, ranking3 = ref3.support_, ref3.ranking_
    # # convert_fields(LIWC, ranking3)

    comm = np.logical_and(support1, support2)
    convert_fields(LIWC, comm)
    pickle.dump(comm, open('data/ed-random-young-common.pick', 'w'))
    # svm_cv(X1[:, support1], y1)
    # svm_cv(X2[:, support2], y2)
    # # svm_cv(X3[:, support3], y3)
    # svm_cv(X1[:, comm], y1)
    # svm_cv(X2[:, comm], y2)
    # svm_cv(X3[:, comm], y3)

    '''Classify with common features'''
    # comm = pickle.load(open('data/common-time.pick', 'r'))
    # print X1[:, comm].shape
    # ref1 = ref(X1[:, comm], y1)
    # ref2 = ref(X2[:, comm], y2)
    # convert_fields(LIWC[comm], ref1.ranking_)
    # convert_fields(LIWC[comm], ref2.ranking_)
    # ref1 = ref(X1, y1)
    # ref2 = ref(X2, y2)
    # convert_fields(LIWC, ref1.ranking_)
    # convert_fields(LIWC, ref2.ranking_)


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


def mlcvrfe():
    cvs = list()
    X, y = load_scale_data('data/ygcolor.data', True)
    print y
    print y[:, 0]
    # refcv = rfecv(X, y[:, 0])
    # pickle.dump(refcv, open('data/posref.pick', 'w'))
    # cvs.append(pickle.load(open('data/posref.pick', 'r')))

    # refcv = rfecv(X, y[:, 1])
    # pickle.dump(refcv, open('data/neuref.pick', 'w'))
    # cvs.append(pickle.load(open('data/neuref.pick', 'r')))
    #
    # refcv = rfecv(X, y[:, 2])
    # pickle.dump(refcv, open('data/negref.pick', 'w'))
    # cvs.append(pickle.load(open('data/negref.pick', 'r')))

    # plot_rfecvs(cvs, ['Positive', 'Neutral', 'Negative'])


def liwc_color_sig():
    X, y = load_scale_data('data/ygcolor.data', True)
    LIWC = iot.read_fields()
    flags = list()
    for yi in y:
        if yi[0]==yi[1] and yi[1]==yi[2]:
            flags.append(True)
        else:
            flags.append(False)
    y = np.array([(b, c, d) for (b, c, d) in y])
    flags = np.array(flags)
    y = y[flags][:, 0]
    yhist, ybin_edges = np.histogram(y, [1, 2, 3, 4])
    print yhist
    y[np.where(y < 3)] = +1
    y[np.where(y==3)] = -1
    print y.shape
    print len(y[np.where(y==1)])
    print len(y[np.where(y==-1)])
    X = X[flags, :]
    print X.shape

    # rfecv1 = rfecv(X, y)
    # pickle.dump(rfecv1, open('data/allrfcv.p', 'w'))
    # rfecv1 = pickle.load(open('data/allrfcv.p', 'r'))
    # scores = list()
    # scores.append(rfecv1)
    # plot_rfecvs(scores, ['All Negative or All Non-negative'])

    ref2 = ref(X, y, 1)
    support2, ranking2 = ref2.support_, ref2.ranking_
    print ranking2
    convert_fields(LIWC, ranking2)


def liwc_color_bar(fieldname):
    X, y = load_scale_data('data/ygcolor.data', True)
    group = 10
    # print X.shape
    y = np.array(y).ravel()
    LIWC = iot.read_fields()
    T = X[:, np.argwhere(LIWC == fieldname).ravel()]
    T = np.repeat(T, 3)
    # fig, ax = plt.subplots()
    print T.shape
    print y.shape
    yhist, ybin_edges = np.histogram(y, [1, 2, 3, 4])
    # print yhist
    xhist, xbin_edges = np.histogram(T, group, range=(np.percentile(T, 2.5), np.percentile(T, 97.5)))
    H = np.histogram2d(T, y, bins=[xbin_edges, ybin_edges])
    print xbin_edges
    ind = np.arange(group)  # the x locations for the groups
    width = 0.35  # the width of the bars: can also be len(x) sequence
    # print H[0][:, 0]
    # print H[0][:, 1]
    # print H[0][:, 2]
    # print H[0][:, 0]+H[0][:, 1]+H[0][:, 2]
    # print xhist
    # print H[0][:, 0]/xhist
    p1 = plt.bar(ind, H[0][:, 0]/xhist, width, color='r', hatch="\\\\")
    p2 = plt.bar(ind, H[0][:, 1]/xhist, width, color='g', hatch="//", bottom=H[0][:, 0]/xhist)
    p3 = plt.bar(ind, H[0][:, 2]/xhist, width, color='b', hatch="--", bottom=(H[0][:, 0] + H[0][:, 1])/xhist)
    plt.xticks(ind+width/2., np.around(0.5*(xbin_edges[1:] + xbin_edges[:-1]), decimals=4))
    # [::3] choose one every three items
    # plt.xticks(ind + width / 2., ind)
    plt.ylabel('Ratio')
    plt.xlabel('Value')
    plt.title('Sentiment class counts of colors by LIWC field ' + fieldname)
    plt.legend((p1[0], p2[0], p3[0]), ('Positive', 'Neutral', 'Negative'))
    plt.show()
    # plt.savefig(fieldname+'-color-ratio.pdf')
    # plt.clf()


def balanced():
    X1, y1 = load_scale_data('data/ed-all-liwc.data')
    # # ref1 = ref(X1, y1, 38)
    # # pickle.dump(ref1, open('data/ref.p', 'wb'))
    # ref1 = pickle.load(open('data/ref.p', 'rb'))
    # rfecv1 = rfecv(X1, y1)
    rfecv2 = rfecv(X1, y1, class_weight='balanced')
    rfecv1 = pickle.load(open('data/rfecv1.pick', 'r'))
    rfecv2 = pickle.load(open('data/rfecv2.pick', 'r'))
    scores = list()
    scores.append(rfecv1.grid_scores_)
    scores.append(rfecv2.grid_scores_)
    plot_rfecvs(scores, ['Non-balanced', 'Balanced'])


def cvrfe():
    ''' evaluate performance with reducing features
    Need a scoring metric'''
    cvs = list()
    '''Accuracy: ed-random-refcv, AUC: ed-random-refcvAUC'''
    # X1, y1 = load_scale_data('data/ed-random.data')
    # refcv = rfecv(X1, y1)
    # pickle.dump(refcv, open('data/ed-random-refcv.pick', 'w'))
    cvs.append(pickle.load(open('data/ed-random-refcv.pick', 'r')))
    #
    # X2, y2 = load_scale_data('data/ed-young.data')
    # refcv2 = rfecv(X2, y2)
    # pickle.dump(refcv2, open('data/ed-young-refcv.pick', 'w'))
    cvs.append(pickle.load(open('data/ed-young-refcv.pick', 'r')))

    # X3, y3 = load_scale_data('data/random-young.data')
    # refcv3 = rfecv(X3, y3)
    # pickle.dump(refcv3, open('data/random-young-refcv.pick', 'w'))
    cvs.append(pickle.load(open('data/random-young-refcv.pick', 'r')))

    plot_rfecvs(cvs, ['ED-Random', 'ED-Younger', 'Random-Younger'])


def cvevluate():
    '''Calculate metrics with cross validations'''
    # X1, y1 = load_scale_data('data/ed-random.data')
    # X2, y2 = load_scale_data('data/ed-young.data')
    X3, y3 = load_scale_data('data/random-young.data')
    # print 'ED-Random'
    # svm_cv(X1, y1)
    # print 'ED-Younger'
    # svm_cv(X2, y2)
    print 'Random-Younger'
    svm_cv(X3, y3)


if __name__ == '__main__':
    cvrfe()
    # plot_rfecvs([pickle.load(open('data/ed-random-refcv.pick', 'r')),
    #              pickle.load(open('data/ed-young-refcv.pick', 'r'))],
    #             ['ED-Random', 'ED-Younger'])
    # common_features()
    # cvevluate()

    '''Common used features'''
    # rank1 = 'Quote; quote_pro; posemo; affect; negemo; OtherP; ingest; Period; Colon; we; AllPct; social_status; friends_count; followers_count; ppron; bio; health; body; sexual; swear; social; money; Dash; information_attractiveness; information_productivity; percept; feel; statuses_count; friends_day; followers_day; relativ; see; hear; leisure; retweet_div; relig; mention_div; conj; Apostro; tweet_pro; dmention_pro; home; i; humans; time; inhib; hashtag_div; auxverb; statuses_day; reply_pro; reply_div; ipron; article; excl; motion; Sixltr; Dic; funct; death; retweet_pro; shehe; they; WC; WPS; past; QMark; Comma; quant; anx; friend; tentat; hashtag_pro; insight; incl; work; sad; anger; achieve; url_pro; family; filler; nonfl; adverb; certain; verb; you; preps; cogmech; SemiC; information_influence; number; pronoun; present; Exclam; future; assent; discrep; cause; Parenth; space; negate; '
    # rank2 = 'ingest; leisure; friends_count; statuses_count; information_productivity; feel; percept; see; hear; dmention_pro; tweet_pro; quote_pro; home; i; information_influence; followers_count; statuses_day; health; bio; work; retweet_pro; mention_div; humans; body; reply_pro; reply_div; relativ; conj; verb; present; sexual; negemo; swear; affect; OtherP; Dash; Colon; Comma; money; death; Exclam; achieve; QMark; url_pro; excl; article; social; relig; funct; preps; ipron; adverb; time; incl; cogmech; space; motion; inhib; social_status; anger; Sixltr; followers_day; Apostro; WPS; Quote; hashtag_div; future; quant; shehe; information_attractiveness; posemo; assent; friend; Parenth; cause; ppron; Dic; number; certain; friends_day; negate; insight; Period; AllPct; past; family; tentat; filler; we; you; they; nonfl; discrep; sad; SemiC; auxverb; anx; pronoun; WC; retweet_div; hashtag_pro; '
    # feature1 = rank1.split(';')
    # feature2 = rank2.split(';')
    # print feature1[:20]
    # print feature2[:20]
    # print list(set(feature1[:20]).intersection(set(feature2[:20])))