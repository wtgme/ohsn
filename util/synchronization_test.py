# -*- coding: utf-8 -*-
"""
Created on 19:31, 02/11/15

@author: wt
"""
import threading
import _multiprocessing
class FetchUrls(threading.Thread):
    """
    Thread checking URLs.
    """

    def __init__(self, urls, output):
        """
        Constructor.

        @param urls list of urls to check
        @param output file to write urls output
        """
        threading.Thread.__init__(self)
        self.urls = urls
        self.output = output

    def run(self):
        """
        Thread run method. Check URLs one by one.
        """
        while self.urls:
            url = self.urls.pop()
            req = urllib2.Request(url)
            try:
                d = urllib2.urlopen(req)
            except urllib2.URLError, e:
                print 'URL %s failed: %s' % (url, e.reason)
            self.output.write(d.read())
            print 'write done by %s' % self.name
            print 'URL %s fetched by %s' % (url, self.name)
