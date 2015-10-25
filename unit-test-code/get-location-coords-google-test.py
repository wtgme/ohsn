# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 10:58:17 2015

initial code snippet borrowed from: 
    
http://stackoverflow.com/questions/14580540/get-location-coordinates-using-bing-or-google-api-in-python

@author: brendan
"""

import urllib
import simplejson

googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

def get_coordinates(query, from_sensor=False):
    query = query.encode('utf-8')
    params = {
        'address': query,
        'sensor': "true" if from_sensor else "false"
    }
    url = googleGeocodeUrl + urllib.urlencode(params)
    json_response = urllib.urlopen(url)
    response = simplejson.loads(json_response.read())
    if response['results']:
        location = response['results'][0]['geometry']['location']
        latitude, longitude = location['lat'], location['lng']
        print query, latitude, longitude
    else:
        latitude, longitude = None, None
        print query, "<no results>"
    return latitude, longitude
    
latitude, longitude = get_coordinates("Southampton", from_sensor=False)
latitude, longitude = get_coordinates("Southampton US", from_sensor=False)
latitude, longitude = get_coordinates("Hell", from_sensor=False)
latitude, longitude = get_coordinates("New York", from_sensor=False)
latitude, longitude = get_coordinates("London", from_sensor=False)