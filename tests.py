#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 11:29:27 2019

@author: kazeem
"""

import unittest
from cirex import create_app, db
from cirex.models import Search, Article, Database, Result
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
