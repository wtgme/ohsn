# -*- coding: utf-8 -*-
"""
Created on 15:26, 06/01/17

@author: wt

This script is to explore that ED friends would lead to users having ED.

"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


from ohsn.util import db_util as dbt
from ohsn.util import io_util as iot
from ohsn.api import profiles_check


