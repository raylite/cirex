#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 11:25:11 2019

@author: kazeem
"""

class commonTerminologies():
    def __init__(self):
        
        self.common_terms = ['randomized', 'randomize', 'randomised', 'randomise', 'random', 'clinical', 
                      'research', 'trial', 'trials', 'affect', 'also', 'control', 'controlled', 'effect', 'human', 
                      'being', 'human being', 'humans','child', 'age', 'young', 'old', 'male', 'female', 'males', 
                      'females', 'child', 'children', 'condition', 'clinic', 'result', 'results', 'clinicaltrials.gov',
                      'gov', 'maintain', 'maintained','treatment', 'treatments', 'care', 'cares', 'self','people', 
                      'patient', 'patients', 'man', 'woman', 'men', 'women', 'use', 'individual', 'individuals', 
                      'person', 'persons', 'author','authors', 'outpatient', 'outpatients']
    
    def __call__(self):
        return list(self.common_terms)