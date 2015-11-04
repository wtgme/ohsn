# -*- coding: utf-8 -*-
"""
Created on 11:55 AM, 11/4/15

@author: wt

"""

from collections import Counter
from lexicons.liwc import Liwc
liwc_lexicon = Liwc()
gettysburg = '''Four score and seven years ago our fathers brought forth on
  this continent a new nation, conceived in liberty, and dedicated to the
  proposition that all men are created equal. Now we are engaged in a great
  civil war, testing whether that nation, or any nation so conceived and so
  dedicated, can long endure. We are met on a great battlefield of that war.
  We have come to dedicate a portion of that field, as a final resting place
  for those who here gave their lives that that nation might live. It is
  altogether fitting and proper that we should do this.'''
# read_document() is a generator, but Counter will consume the whole thing
category_counts = Counter(liwc_lexicon.read_document(gettysburg))
print 'Basic category counts: {}'.format(category_counts)
# print out a tabulation that looks like the LIWC software's text report
full_counts = liwc_lexicon.summarize_document(gettysburg)
liwc_lexicon.print_summarization(full_counts)