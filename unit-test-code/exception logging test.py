# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 08:19:06 2015



@author: home
"""


import datetime

ERROR_LOG_FILENAME = 'TAPI_TimelineHarvester_ErrorLog_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.log'
# ERROR_LOG_FILENAME = 'TAPI_TimelineHarvester_ErrorLog 08:30.log'


errorfile = open(ERROR_LOG_FILENAME, 'w')

try:
       test = {}
       print test['missing']
except Exception, e:
    error = "ERROR" + "\t" + "get_pictures()\t" + str(e.__class__) +"\t"+ str(e) 
    errorfile.write(error)
    errorfile.flush()
    pass