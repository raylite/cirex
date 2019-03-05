# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 17:49:54 2017

@author: CR107
"""
try:
    import urllib2
except:
    import urllib.request as urllib2

DEFAULT_AGENT = 'get_ref'

class setUrl:
    def __init__(self, url = None, user_agent=DEFAULT_AGENT):
        self.data = None
        
    def __call__(self, url):
        headers = {'User-agent': DEFAULT_AGENT}
        print (url)
        request = urllib2.Request(url, self.data, headers or {})
        res = urllib2.urlopen(request)
        new_url = res.geturl()
    
        return new_url