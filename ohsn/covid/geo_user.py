import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
from ohsn.api import tweet_lookup 
import ohsn.util.io_util as iot
import pymongo
import pandas as pd



df = pd.read_csv('/home/wt/Code/ohsn/ohsn/covid/us_geo.csv')
tids = df['Tweet_ID'].tolist()
tids = [str(int(i)) for i in tids]
print len(tids)
print(tids[:2])


dbname = 'covid'
colname = 'geo_user'
db = dbt.db_connect_no_auth(dbname)
com = db[colname]

com.create_index([('user.id', pymongo.ASCENDING),
                    ('id', pymongo.DESCENDING)])
com.create_index([('id', pymongo.ASCENDING)], unique=True)

i = 0
while 100 * i < len(tids):
    ids = tids[i*100: (i+1)*100]
    print(i*100, (i+1)*100)
    tweets = tweet_lookup.get_tweets_info(ids)
    for tweet in tweets:
        try:
            com.insert(tweet)
        except pymongo.errors.DuplicateKeyError:
            pass
    i += 1
