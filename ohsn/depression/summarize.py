import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.db_util as dbt
import ohsn.util.io_util as io

def out_tweet(dbname, colname):
    # out depression tweets
    tweets = dbt.db_connect_col(dbname, colname)
    for tweet in tweets.find({}, no_cursor_timeout=True):
        text = tweet['text'].encode('utf8')
        print str(tweet['id']) + '\t' + text


if __name__ == '__main__':
    out_tweet('depression', 'search')
