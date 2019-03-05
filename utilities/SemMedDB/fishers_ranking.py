#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 13:09:55 2018

@author: kazeem
"""

import pandas as pd
import scipy.stats as stats
from . import semmeddb_accessor as sdb
from statsmodels.stats.multitest import multipletests
#from statsmodels.sandbox.stats.multicomp import multipletests as mt
import os

from utilities import tfidf_ranking

root = os.path.abspath(os.path.dirname(__file__))

def analyse_semmed_predicates(pmids):
    unique_fishers = 0
    unique_chi2 = 0
    nonunique_fishers = 0
    nonunique_chi2 = 0
    unique_tfidf = 0
    nonunique_tfidf = 0
       
    unique_pred_details, nonunique_pred_details, tfidf_predicates = sdb.load_sub_preds(pmids)
    
    unique_fishers, unique_chi2 = chi_fishers_ranking(unique_pred_details)
    nonunique_fishers, nonunique_chi2 = chi_fishers_ranking(nonunique_pred_details, unique = False)
    nonunique_tfidf = tfidf_ranking.compute_tfidf(tfidf_predicates['SUBJ_OBJ_COMBINED'], unique = False)#predicates tfidf fix by making non unique multigrams
    unique_tfidf = tfidf_ranking.compute_tfidf(tfidf_predicates['UNIQUE_SUBJ_OBJ_COMBINED'], unique = True)
    
    return unique_fishers, unique_chi2, nonunique_fishers, nonunique_chi2, nonunique_tfidf, unique_tfidf
    
    
def chi_fishers_ranking(preds_details, unique = True):  
    if unique:
        db_record = pd.read_csv(os.path.join(root, 'unique_predicates.csv'))
    else:
        db_record = pd.read_csv(os.path.join(root, 'multigram_predicates.csv'))
    
    global_sum = db_record['Frequency'].sum()
    
    local_sum = preds_details['Frequency'].sum()
    
    
    preds_details = preds_details.sort_values(by = 'Predicate').reset_index(drop=True)
        
    ix = db_record['Predicate'].isin(preds_details['Predicate']).tolist()
    
    ix = map(lambda x : x[0],filter(lambda x : x[1]==False,list(enumerate(ix))))
    
    global_freq = db_record.drop(ix).sort_values(by='Predicate').reset_index(drop=True)
    
    preds_details['DB_frequency'] = global_freq['Frequency']
        
    preds_details['fishers'] = preds_details.apply(lambda x: stats.fisher_exact([[local_sum, global_sum],
                                                                                [x['Frequency'], x['DB_frequency']]])[1],
                                                    axis=1)#fishers returns a tuple, only the p value is selected
    preds_details['chi_contingency'] = preds_details.apply(lambda x: stats.chi2_contingency([[local_sum, global_sum],
                                                                                [x['Frequency'], x['DB_frequency']]])[1], 
                                                    axis=1)
    
    preds_details = preds_details.sort_values(by='fishers', ascending=True).reset_index(drop=True)

    corrected_f_pvalues = multipletests(preds_details['fishers'], alpha = 0.05, method = 'fdr_bh', is_sorted = True)[1]
    corrected_chi_pvalues = multipletests(preds_details['chi_contingency'], alpha = 0.05, method = 'fdr_bh', is_sorted = True)[1]
    
    if not unique:
        fisher_values_df = pd.DataFrame({'Nu_F_Predicates': preds_details['Predicate'],
                                   'fishers': preds_details['fishers'],
                                   'corrected_f_p_value': corrected_f_pvalues,
                                   'Docs_count': preds_details['Doc_count']
                                   }).sort_values(by='corrected_f_p_value', ascending=False).reset_index(drop=True)
        chi_values_df = pd.DataFrame({'Nu_Chi2_Predicates': preds_details['Predicate'],
                                   'chi': preds_details['chi_contingency'],
                                   'chi_corrected': corrected_chi_pvalues
                               }).sort_values(by='chi_corrected', ascending=False).reset_index(drop=True)
    
    else:
        fisher_values_df = pd.DataFrame({'Un_F_Predicates': preds_details['Predicate'],
                                   'fishers': preds_details['fishers'],
                                   'corrected_f_p_value': corrected_f_pvalues,
                                   'Docs_Count': preds_details['Frequency']
                                   }).sort_values(by='corrected_f_p_value', ascending=False).reset_index(drop=True)
        chi_values_df = pd.DataFrame({'Un_Chi2_Predicates': preds_details['Predicate'],
                                   'chi': preds_details['chi_contingency'],
                                   'chi_corrected': corrected_chi_pvalues
                               }).sort_values(by='chi_corrected', ascending=False).reset_index(drop=True)
    
    
    return fisher_values_df, chi_values_df


    
    
    
    