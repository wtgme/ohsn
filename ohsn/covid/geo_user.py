import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
from ohsn.api import tweet_lookup 
import ohsn.util.io_util as iot
import pymongo
import pandas as pd
import json
import pandas as pd


# Collect data
def collect_tweets():
    # df = pd.read_csv('/home/wt/Code/ohsn/ohsn/covid/us_geo.csv')
    df = pd.read_csv('/home/wt/Desktop/Antonella/geo-detail-2020.csv')
    tids = df['Tweet_ID'].tolist()
    tids = [str(int(i)) for i in tids]
    print(len(tids))
    print(tids[:2])


    dbname = 'covid'
    colname = 'geo_user_2020'
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


def export_tweets():
    dbname = 'covid'
    colname = 'geo_user_2020'
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    data = []
    for doc in com.find({}):
        for tag in (doc['entities']['hashtags']):
            data.append([doc['id'], tag, doc['created_at']])
    
    df = pd.DataFrame(data, columns=['Tweet_ID', 'Hashtag', 'Date'])
    df.to_csv('./ohsn/covid/geo_user_tags_2020.csv', index=None) 


    # json.dump(data, open('./ohsn/covid/geo_user_2020.json', 'w'))


export_tweets()