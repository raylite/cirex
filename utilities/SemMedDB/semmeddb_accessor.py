# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 14:44:30 2018

@author: ja18581
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 14:44:30 2018

@author: ja18581
"""
import sqlite3
import pandas as pd
from collections import Counter
from nltk.corpus import stopwords
import re
import string
import os

from common_terms import commonTerminologies

root = os.path.abspath(os.path.dirname(__file__))

path = os.path.join(root, 'full_merged.db')
  

def count_predicates(grams_counter, predicate):
    pattern = re.compile("^\s+|\s*,|;|\|\s*|\s+$")
    #stemmer = PorterStemmer()
    common_terms = commonTerminologies().common_terms#local class defining frequent terms
    sw = set(stopwords.words('english') + common_terms + list(string.punctuation)) 
    
    grams_tokenizer = [grams.lower() for grams in pattern.split(predicate) if not grams.lower() in sw]#multigram split based on comma
    for grams in grams_tokenizer:
        grams_counter[grams] += 1
            
    return grams_counter
            

def counter_to_df(predicates_count):
    grams_pred_list = []
    grams_count_list = []
    
    for gpred, gcount in predicates_count.items():
        grams_pred_list.append(gpred)
        grams_count_list.append(gcount)
  
    grams_pred_df = {'Predicate': grams_pred_list, 'Frequency': grams_count_list}
    grams_pred_df = pd.DataFrame(grams_pred_df)
    return grams_pred_df
    


def subset_df(ids):
    conn = sqlite3.connect(path)
    query =  "SELECT PMID, UP_SUBJ_OBJ_COMBINED, NUP_SUBJ_OBJ_COMBINED FROM merged_subj_obj WHERE merged_subj_obj.PMID IN (%s)" % ','.join([str(i) for i in ids])
    record = pd.read_sql_query(query, conn)
    return record
    
    
def count_pred(record, col):
    predicates_counter_multigrams = Counter()
        
    for predicates in record[col]:
        grams_predicates_count = count_predicates(predicates_counter_multigrams, predicates)
    pred_count = counter_to_df(grams_predicates_count)
    return pred_count


def load_sub_preds(pmids):
       
    predicates = subset_df(pmids)
    
    unique_grams_frq = count_pred(predicates, col = 'NUP_SUBJ_OBJ_COMBINED')
    
    nonunique_grams_frq = count_pred(predicates, col = 'UP_SUBJ_OBJ_COMBINED')
        
    return unique_grams_frq, nonunique_grams_frq, predicates[['UP_SUBJ_OBJ_COMBINED','NUP_SUBJ_OBJ_COMBINED']]


