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

infilename = 'mrredges-no-tweet-no-retweet.csv'
infile = open(infilename, 'r')
csv_infile_edges = csv.reader(infile)

#skip the headers
next(csv_infile_edges, None)

outfilename = 'mrredges-no-tweet-no-retweet-poi-counted.csv'
outfile = open(outfilename, 'w')
outfile.write("id0,id1,relationship,count\n")

edges = dict()

for row in csv_infile_edges:
	try:
		if row[0] != row[1]:
			edges[row[0] + row[2] + row[1]]['value'] += 1
	except KeyError:
		print "new key added:" + row[0] + row[2] + row[1]
		edges[row[0] + row[2] + row[1]] = {}
		edges[row[0] + row[2] + row[1]]['id0'] = row[0]
		edges[row[0] + row[2] + row[1]]['id1'] = row[1]
		edges[row[0] + row[2] + row[1]]['relationship'] = row[2]
		edges[row[0] + row[2] + row[1]]['value'] = 1

for key in edges:
	print edges[key]['id0'] +" "+ edges[key]['id1'] +" "+ edges[key]['relationship'] +" "+ str(edges[key]['value']) 
	outfile.write( edges[key]['id0'] +","+ edges[key]['id1'] +","+ edges[key]['relationship'] +","+ str(edges[key]['value']) + "\n")
	
		

