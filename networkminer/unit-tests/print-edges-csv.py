# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 20:16:48 2015

This parses the tweets in the timelines db for mentions/replies/retweets 
and creates edges in the mrredges collection.

@author: brendan
"""
import pymongo
import datetime
import csv
import array

infilename_edges = 'mrredges.csv'
infilename_poi = 'poi.csv'
outfilename = 'mrredges-no-tweet-no-retweet.csv'

infile_edges = open(infilename_edges, 'r')
infile_poi = open(infilename_poi, 'r')
outfile = open(outfilename, 'w')

outfile.write("id0,id1,relationship,first-date,statusid\n")
# only interested in reply and and mentions

csv_infile_edges = csv.reader(infile_edges)
csv_infile_poi = csv.reader(infile_poi)
csv_writer = csv.writer(outfile)

#skip the headers
next(csv_infile_edges, None)
next(csv_infile_poi, None)

poi = set()
for row in csv_infile_poi:
	poi.add(long(row[0]))

# print poi

for row in csv_infile_edges:
  if row[2] != "tweet":
	if row[2] != "retweet":
		# print row[0]
		if (long(row[0]) in poi) and (long(row[1]) in poi):
		#if row[0] == "518335800":
			# print row
			csv_writer.writerow(row)
		

