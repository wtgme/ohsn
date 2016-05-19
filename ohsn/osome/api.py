# -*- coding: utf-8 -*-
"""
Created on 10:54 PM, 5/18/16

@author: tw
"""
import unirest
import urllib
import ssl

# unirest.timeout(10)
def callback_function(response):
    print '---------------------------------------------------------------'
    print response.code # The HTTP status code
    print response.headers # The HTTP headers
    print response.body # The parsed response
    print response.raw_body # The unparsed response


def time_series(start, end, q):
    '''
    Time Series
    A count of the number of tweets per day matching the query.
    '''
    print '-------------------------------------'
    print 'Time Series:', start, end, q
    start = urllib.quote(start.encode('utf8'))
    end = urllib.quote(end.encode('utf8'))
    q = urllib.quote(q.encode('utf8'))
    response = unirest.get("https://osome-public.p.mashape.com/time-series?",
      headers={
        "X-Mashape-Key": "G8LtuZOPOwmshZf6jTvEGxob5QuZp10kxV4jsnAvnOb4uilKkG",
        "Accept": "application/json"
      },
      params={"start": start, "end": end, "q": q}
    )
    print response.code # The HTTP status code
    print response.headers # The HTTP headers
    print response.body # The parsed response


def tweet_count(start, end, q):
    '''
    Tweet Counts
    For each element in the query, returns the number of tweets containing that element.
    '''
    print '-------------------------------------'
    print 'Tweet Counts:', start, end, q
    start = urllib.quote(start.encode('utf8'))
    end = urllib.quote(end.encode('utf8'))
    q = urllib.quote(q.encode('utf8'))
    response = unirest.get("https://osome-public.p.mashape.com/counts?",
      headers={
        "X-Mashape-Key": "G8LtuZOPOwmshZf6jTvEGxob5QuZp10kxV4jsnAvnOb4uilKkG",
        "Accept": "application/json"
      },
      params={"start": start, "end": end, "q": q}
    )
    print response.code # The HTTP status code
    print response.headers # The HTTP headers
    print response.body # The parsed response


def tweet_ids(start, end, q):
    '''
    Tweet IDs
    Retrieve a list of Tweet IDs matching any element of the query.
    '''
    print '-------------------------------------'
    print 'Tweet IDs:', start, end, q
    start = urllib.quote(start.encode('utf8'))
    end = urllib.quote(end.encode('utf8'))
    q = urllib.quote(q.encode('utf8'))
    print start, end, q
    response = unirest.get("https://osome-public.p.mashape.com/tweet-id?",
        headers={
            "X-Mashape-Key": "G8LtuZOPOwmshZf6jTvEGxob5QuZp10kxV4jsnAvnOb4uilKkG",
            "Accept": "application/json"
        },
      params={ "start": start, "end": end, "q": q}
    )
    print response.code # The HTTP status code
    print response.headers # The HTTP headers
    print response.body # The parsed response

def post_count(start, end, q):
    '''User Post Count
    Count the number of tweets from each user with at least one tweet matching the query.
    '''
    print '-------------------------------------'
    print 'User Post Count:', start, end, q
    start = urllib.quote(start.encode('utf8'))
    end = urllib.quote(end.encode('utf8'))
    q = urllib.quote(q.encode('utf8'))
    response = unirest.get("https://osome-public.p.mashape.com/user-post-count?",
      headers={
        "X-Mashape-Key": "G8LtuZOPOwmshZf6jTvEGxob5QuZp10kxV4jsnAvnOb4uilKkG",
        "Accept": "application/json"
      },
      params={ "start": start, "end": end, "q": q}
    )
    print response.code # The HTTP status code
    print response.headers # The HTTP headers
    print response.body # The parsed response

if __name__ == '__main__':
    # time_series('2011-01-01', '2016-05-01', '#eatingdisorder')
    keywords = ['eating disorder', 'eatingdisorder', 'anorexia', 'bulimia', 'anorexic',
                'ana', 'bulimic', 'anorexia nervosa', 'mia', 'thinspo',
                'bulemia', 'purge', 'bulimia nervosa', 'binge',  'selfharm',
                'ednos', 'edprobs', 'edprob', 'proana', 'anamia', 'promia',
                'askanamia', 'bonespo', 'legspo']
    postlist = []
    for keyword in keywords:
        keyword = keyword.replace(" ", "")
        keyword = '#'+keyword
        postlist.append(keyword)
        time_series('2011-01-01', '2016-05-01', keyword)
        post_count('2011-01-01', '2016-05-01', keyword)
        # tweet_ids('2011-01-01', '2016-05-01', keyword)
    tweet_count('2011-01-01', '2016-05-01', ','.join(postlist))

    # print unirest.get("http://osome.iuni.iu.edu/moe/api/mashape/result/5c642c44-3ed9-4513-8d9e-ebec23b758da")