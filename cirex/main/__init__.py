#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 17:32:50 2018

@author: kazeem
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from cirex.main import views
