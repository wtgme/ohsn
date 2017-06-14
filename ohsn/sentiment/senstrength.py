# -*- coding: utf-8 -*-
"""
Created on 15:25, 14/04/17

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import os
import shlex, subprocess

# java -jar SentiStrengthCom.jar sentidata SentiStrength_DataEnglishFeb2017/ input tweets.txt scale annotateCol 3 overwrite
# java -jar SentiStrengthCom.jar sentidata SentiStrength_DataEnglishFeb2017/ input retweet.txt scale annotateCol 3 overwrite
def rate_sentiment(sentiString):
    # Return positive negative neutral tuple
    MYDIR = os.path.dirname(__file__)
    #open a subprocess using shlex to get the command line string into the correct args list format
    p = subprocess.Popen(shlex.split('java -jar '+os.path.join(MYDIR,'SentiStrengthCom.jar')+' stdin sentidata '
                                 + os.path.join(MYDIR, 'SentiStrength_DataEnglishFeb2017/ scale')),
                     stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #communicate via stdin the string to be rated. Note that all spaces are replaced with +
    stdout_text, stderr_text = p.communicate(sentiString.replace(" ", "+"))
    #remove the tab spacing between the positive and negative ratings. e.g. 1    -5 -> 1-5
    # stdout_text = stdout_text.rstrip().replace("\t", "")
    return [int(v) for v in stdout_text.rstrip().split()]

if __name__ == '__main__':
    print rate_sentiment('Everynight I hope i wake up thinner, at my UGW. One day it will happen.')
    print rate_sentiment('I talk to YOU')