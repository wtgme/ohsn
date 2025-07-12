# -*- coding: utf-8 -*-
"""
Created on 7:53 PM, 2/19/16

@author: tw
The util for statistics

"""
import numpy as np
import math
import scipy.stats as stats


def mannwhitneyu(x, y, use_continuity=True, alternative=None):
    """
    Computes the Mann-Whitney rank test on samples x and y.

    Parameters
    ----------
    x, y : array_like
        Array of samples, should be one-dimensional.
    use_continuity : bool, optional
            Whether a continuity correction (1/2.) should be taken into
            account. Default is True.
    alternative : None (deprecated), 'less', 'two-sided', or 'greater'
            Whether to get the p-value for the one-sided hypothesis ('less'
            or 'greater') or for the two-sided hypothesis ('two-sided').
            Defaults to None, which results in a p-value half the size of
            the 'two-sided' p-value and a different U statistic. The
            default behavior is not the same as using 'less' or 'greater':
            it only exists for backward compatibility and is deprecated.

    Returns
    -------
    statistic : float
        The Mann-Whitney U statistic, equal to min(U for x, U for y) if
        `alternative` is equal to None (deprecated; exists for backward
        compatibility), and U for y otherwise.
    pvalue : float
        p-value assuming an asymptotic normal distribution. One-sided or
        two-sided, depending on the choice of `alternative`.

    Notes
    -----
    Use only when the number of observation in each sample is > 20 and
    you have 2 independent samples of ranks. Mann-Whitney U is
    significant if the u-obtained is LESS THAN or equal to the critical
    value of U.

    This test corrects for ties and by default uses a continuity correction.

    """
    if alternative is None:
        print("Calling `mannwhitneyu` without specifying "
                      "`alternative` is deprecated.", DeprecationWarning)

    x = np.asarray(x)
    y = np.asarray(y)
    n1 = len(x)
    n2 = len(y)
    ranked = stats.rankdata(np.concatenate((x, y)))
    rankx = ranked[0:n1]  # get the x-ranks
    u1 = n1*n2 + (n1*(n1+1))/2.0 - np.sum(rankx, axis=0)  # calc U for x
    u2 = n1*n2 - u1  # remainder is U for y
    T = stats.tiecorrect(ranked)
    if T == 0:
        raise ValueError('All numbers are identical in mannwhitneyu')
    sd = np.sqrt(T * n1 * n2 * (n1+n2+1) / 12.0)

    meanrank = n1*n2/2.0 + 0.5 * use_continuity
    if alternative is None or alternative == 'two-sided':
        bigu = max(u1, u2)
    elif alternative == 'less':
        bigu = u1
    elif alternative == 'greater':
        bigu = u2
    else:
        raise ValueError("alternative should be None, 'less', 'greater' "
                         "or 'two-sided'")

    z = (bigu - meanrank) / sd
    if alternative is None:
        # This behavior, equal to half the size of the two-sided
        # p-value, is deprecated.
        p = stats.distributions.norm.sf(abs(z))
    elif alternative == 'two-sided':
        p = 2 * stats.distributions.norm.sf(abs(z))
    else:
        p = stats.distributions.norm.sf(z)

    u = u2
    # This behavior is deprecated.
    if alternative is None:
        u = min(u1, u2)
    # print stats.MannwhitneyuResult(u, p)
    return z


def central_data(data):
    maxv = np.percentile(data, 97.5)
    minv = np.percentile(data, 2.5)
    return [x for x in data if minv < x < maxv]


def z_test(list1, list2):
    # z-test for two lists
    n1, n2 = len(list1), len(list2)
    mu1, mu2 = np.mean(list1), np.mean(list2)
    s1, s2 = np.std(list1), np.std(list2)
    z = (mu1-mu2)/(np.sqrt(s1**2/n1 + s2**2/n2))
    from scipy.stats import norm
    pval = 2*(1 - norm.cdf(abs(z)))
    return n1, n2, z, pval


def ks_test(list1, list2, n=1):
    d, p = stats.ks_2samp(list1, list2)
    return len(list1), len(list2), (d), (p*n)

def ttest(list1, list2, n=1):
    d, p = stats.ttest_ind(list1, list2)
    return np.mean(list1), np.std(list1), np.mean(list2), np.std(list2), (d), p, (p*n)

def utest(list1, list2, n=1):
    # return mean, std, mean, std, U, P, P-core, Z
    d, p = stats.mannwhitneyu(list1, list2, alternative='two-sided')
    z = mannwhitneyu(list1, list2, alternative='greater')
    return np.mean(list1), np.std(list1), np.mean(list2), np.std(list2), (d), p, (p*n), z

def wtest(list1, list2, n=1):
    d, p = stats.wilcoxon(list1, list2)
    return np.mean(list1), np.mean(list2), (d), p, (p*n)

def comm_stat(lista):
    # return the min, max, mean and std
    return (np.amin(lista)), (np.amax(lista)), (np.mean(lista)), (np.std(lista))


def mode(lst):
    # find the mode of a list
    return max(set(lst), key=lst.count)


def tau_coef(x1, x2):
    tau, p_value = stats.kendalltau(x1, x2)
    return (tau, p_value)


def pearson(x, y):
    # calculate the pearson correlation of two list
    # n = len(x)
    # avg_x = float(sum(x))/n
    # avg_y = float(sum(y))/n
    # diffprod = 0.0
    # xdiff2 = 0.0
    # ydiff2 = 0.0
    # for idx in range(n):
    #     xdiff = x[idx] - avg_x
    #     ydiff = y[idx] - avg_y
    #     diffprod += xdiff*ydiff
    #     xdiff2 += xdiff*xdiff
    #     ydiff2 += ydiff*ydiff
    # return diffprod/math.sqrt(xdiff2*ydiff2)
    return stats.pearsonr(x, y)



if __name__ == '__main__':
    l1 = [1,2,6,7,8,10,3,4,5,9]
    l2 = [1,2,3,4,5,6,7,8,9,10]
    print z_test(l1, l2)
    print ks_test(l1, l2)
    print pearson(l1, l2)
    print stats.pearsonr(l1, l2)