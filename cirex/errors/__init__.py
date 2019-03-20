#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 17:32:50 2018

@author: kazeem
"""

from flask import Blueprint

bp = Blueprint('errors', __name__)

from cirex.errors import handlers