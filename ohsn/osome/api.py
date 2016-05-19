# -*- coding: utf-8 -*-
"""
Created on 10:54 PM, 5/18/16

@author: tw
"""
import unirest
import urllib


def callback_function(response):
    print response.code # The HTTP status code
    print response.headers # The HTTP headers
    print response.body # The parsed response
    print response.raw_body # The unparsed response


def time_series(start, end, q):
    '''
    Time Series
    A count of the number of tweets per day matching the query.
    '''
    start = urllib.quote(start.encode('utf8'))
    end  = urllib.quote(end.encode('utf8'))
    q = urllib.quote(q.encode('utf8'))
    response = unirest.get("https://osome-public.p.mashape.com/time-series?",
      headers={
        "X-Mashape-Key": "G8LtuZOPOwmshZf6jTvEGxob5QuZp10kxV4jsnAvnOb4uilKkG",
        "Accept": "application/json"
      },
      params={"start": start, "end": end, "q": q},
      callback=callback_function
    )

time_series('2016-01-01T00:00:00', '2016-01-03T23:59:59', '#yolo,#swag')

def tweet_count(start, end, q):
    '''
    Tweet Counts
    For each element in the query, returns the number of tweets containing that element.
    '''
    start = urllib.quote(start.encode('utf8'))
    end  = urllib.quote(end.encode('utf8'))
    q = urllib.quote(q.encode('utf8'))
    response = unirest.get("https://osome-public.p.mashape.com/counts?",
      headers={
        "X-Mashape-Key": "G8LtuZOPOwmshZf6jTvEGxob5QuZp10kxV4jsnAvnOb4uilKkG",
        "Accept": "application/json"
      },
      params={ "start": start, "end": end, "q": q}, callback=callback_function
    )


def tweet_ids(start, end, q):
    '''
    Tweet IDs
    Retrieve a list of Tweet IDs matching any element of the query.
    '''
    start = urllib.quote(start.encode('utf8'))
    end  = urllib.quote(end.encode('utf8'))
    q = urllib.quote(q.encode('utf8'))
    response = unirest.get("https://osome-public.p.mashape.com/tweet-id?",
      headers={
        "X-Mashape-Key": "G8LtuZOPOwmshZf6jTvEGxob5QuZp10kxV4jsnAvnOb4uilKkG",
        "Accept": "application/json"
      },
      params={ "start": start, "end": end, "q": q}, callback=callback_function
    )


def post_count(start, end, q):
    '''User Post Count
    Count the number of tweets from each user with at least one tweet matching the query.
    '''
    start = urllib.quote(start.encode('utf8'))
    end  = urllib.quote(end.encode('utf8'))
    q = urllib.quote(q.encode('utf8'))
    response = unirest.get("https://osome-public.p.mashape.com/user-post-count?",
      headers={
        "X-Mashape-Key": "G8LtuZOPOwmshZf6jTvEGxob5QuZp10kxV4jsnAvnOb4uilKkG",
        "Accept": "application/json"
      },
      params={ "start": start, "end": end, "q": q}, callback=callback_function
    )

if __name__ == '__main__':
    # time_series('2016-01-01T00:00:00', '2016-01-03T23:59:59', '#yolo,#swag')
 # "job_id": "97e283aa-7d1f-42bc-9e77-e125b04d7e8f",
 #  "result_url": "http://osome.iuni.iu.edu/moe/api/mashape/result/97e283aa-7d1f-42bc-9e77-e125b04d7e8f"

    print unirest.get("http://osome.iuni.iu.edu/moe/api/mashape/result/5c642c44-3ed9-4513-8d9e-ebec23b758da")