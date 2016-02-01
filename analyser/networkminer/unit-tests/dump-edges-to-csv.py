# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 20:16:48 2015

This parses the tweets in the timelines db for mentions/replies/retweets 
and creates edges in the mrredges collection.

@author: brendan
"""

import pymongo
import datetime

MONGOURL = 'localhost'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
POI_COL = 'poi'
MRR_COL = 'mrredges'
WeightedEdges_COL = 'mrredges_aggregated'

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    
    poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL

    mrredges = db[MRR_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + MRR_COL

except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()

# only interested in reply and retweet and mentions

print 'mentioned\t' + str(mrredges.find({'relationship':'mentioned'}).count())
print 'reply-to\t' + str(mrredges.find({'relationship':'reply-to'}).count())
print "retweets\t" + str(mrredges.find({'relationship':'retweet'}).count())
print 'mentioned\t' + str(mrredges_counted.find({'relationship':'mentioned'}).count())
print 'reply-to\t' + str(mrredges_counted.find({'relationship':'reply-to'}).count())
print "retweets\t" + str(mrredges_counted.find({'relationship':'retweet'}).count())

edge = mrredges.find({'count':None}).limit(1)[0]

while edge:
	
	# print edge['id0'], edge['id1']
	
	edges_count = mrredges.find({'id0':edge['id0'], 'id1': edge['id1'],'relationship': edge['relationship'] }).count()

	agg_edge = dict()
	agg_edge['id0'] = edge['id0']
	agg_edge['id1'] = edge['id1']
	agg_edge['relationship'] = edge['relationship']
	agg_edge['count'] = edges_count

	mrredges_counted.insert(agg_edge)
	mrredges.update({'id0':edge['id0'], 'id1': edge['id1'],'relationship': edge['relationship']}, {'$set':{"count": edges_count}}, multi=True)

	edge = mrredges.find({'count':None}).limit(1)[0]


print 'mentioned\t' + str(mrredges.find({'relationship':'mentioned'}).count())
print 'reply-to\t' + str(mrredges.find({'relationship':'reply-to'}).count())
print "retweets\t" + str(mrredges.find({'relationship':'retweet'}).count())
print 'mentioned\t' + str(mrredges_counted.find({'relationship':'mentioned'}).count())
print 'reply-to\t' + str(mrredges_counted.find({'relationship':'reply-to'}).count())
print "retweets\t" + str(mrredges_counted.find({'relationship':'retweet'}).count())

exit()

