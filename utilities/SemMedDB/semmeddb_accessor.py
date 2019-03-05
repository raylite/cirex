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

import pandas as pd
from collections import Counter
from nltk.corpus import stopwords
import re
import string
import os

from common_terms import commonTerminologies

root = os.path.abspath(os.path.dirname(__file__))

path = os.path.join(root, 'merged_semmeddb_record.csv')
  
heading = ["PMID", "SUBJECT_NAME", "OBJECT_NAME", "UNIQUE_SUBJECT_COMBINED", "UNIQUE_OBJECT_COMBINED",
           "UNIQUE_SUBJ_OBJ_COMBINED", "SUBJECT_COMBINED", "OBJECT_COMBINED", "SUBJ_OBJ_COMBINED"]
    
def count_predicates(grams_counter, predicate):
    pattern = re.compile("^\s+|\s*,\s*|\s+$")
    #stemmer = PorterStemmer()
    common_terms = commonTerminologies()#local class defining frequent terms
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
    


def subset_df(cols, ids):
    chunksize = 10**5
    rec = pd.read_csv(path, index_col = False, header = None, names = heading, usecols = cols, chunksize = chunksize)
    
    record = pd.concat([chunk[chunk['PMID'].isin(ids)] for chunk in rec]).reset_index(drop=True)
    
    return record
    
    
def count_nonunique_pred(record):
    predicates_counter_multigrams = Counter()
    doc_counter = Counter()
    
    #record = aggregate_df(cols, ids, False)
    
    for predicates in record['SUBJ_OBJ_COMBINED']:
        grams_predicates_count = count_predicates(predicates_counter_multigrams, predicates)
    ngrams_count = counter_to_df(grams_predicates_count)
    
    for predicates in record['UNIQUE_SUBJ_OBJ_COMBINED']:##to detrmine the number of documents containing aech predicate
        predicate_doc_count = count_predicates(doc_counter, predicates)
    docs_count = counter_to_df(predicate_doc_count)
    docs_count.rename(index = str, columns = {'Predicate': 'Predicate', 'Frequency': 'Doc_count'}, inplace=True)
    
    ngrams_count = pd.merge(ngrams_count, docs_count, on = 'Predicate')
    return ngrams_count
    
def count_unique_pred(record):
    predicates_counter_multigrams = Counter()
        
   
    for predicates in record['UNIQUE_SUBJ_OBJ_COMBINED']:
        grams_predicates_count = count_predicates(predicates_counter_multigrams, predicates)
    ngrams_frq_count = counter_to_df(grams_predicates_count)
    return ngrams_frq_count
    


def load_sub_preds(pmids):
    cols_to_fetch = ['PMID', 'UNIQUE_SUBJ_OBJ_COMBINED', 'SUBJ_OBJ_COMBINED']
    
    predicates = subset_df(cols_to_fetch, pmids)
    
    unique_grams_frq_avg = count_unique_pred(predicates)
    
    nonunique_grams_frq_avg = count_nonunique_pred(predicates)
    
    return unique_grams_frq_avg, nonunique_grams_frq_avg, predicates[['UNIQUE_SUBJ_OBJ_COMBINED','SUBJ_OBJ_COMBINED']]


# =============================================================================
# =============================================================================
# if __name__=='__main__':
#      f = open('citation.txt').readlines()
#      f = [x.strip('\n') for x in f]
#      v = load_merged_preds(f)
# =============================================================================
# =============================================================================