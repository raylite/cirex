# -*- coding: utf-8 -*-
"""
Created on Wed Oct 03 13:38:34 2018

@author: raylite
"""
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#from stopwords import bigram
from nltk.util import ngrams
import SemMedDB.common_terms as ct
import re


doc_dict = defaultdict(list)
freq_counter = Counter()

def unigram(data, field):
    pattern = re.compile("^\s+|\s*,|;|\|\s*|\s+$")
    terms = ct.commonTerminologies()
    common_terms = terms.common_terms 
    stoplist = set(stopwords.words('english') + common_terms + list(string.punctuation))
    
    if field == 'mesh':
        tokens = []
        for (i,row) in data.iterrows():
            for mesh in pattern.split(str(row['MeSH'])):
               if mesh.lower().strip() not in stoplist:
                   mesh = mesh.lower().strip()
                   doc_dict[mesh].append(row['PMID'])
                   freq_counter[mesh] += 1
                   
        return freq_counter, doc_dict
               
    elif field == 'tiabs':
        df = pd.concat([data['Title'], data['Abstract']])
        tokens = word_tokenize(df.str.cat(sep = ' ').lower())
        
        translator = str.maketrans('', '', string.punctuation+string.digits)#python 3
        tokens = [token.translate(translator) for token in tokens]
        
        tokens = [token for token in tokens if token and token not in stoplist and len(token) > 3] #removes any None element
        return tokens

def bigrams(data, field, n=2):
    bigrams = ngrams(unigram(data, field), n)
    return [' '.join(grams) for grams in bigrams] 

def create_freq_dict(tokens_list):
    frequency_dict = Counter(tokens_list)
    
    return frequency_dict

def sortKey(tokenslist):
    return tokenslist[1]


def sort_dict(tokens_dict):
    mean = np.mean(list(tokens_dict.values()))
    sorted_tokens_list = [(key, value) for key, value in list(tokens_dict.items()) if value >= round(mean)]##cut off point set
    sorted_tokens_list.sort(reverse = True, key = sortKey)
    return sorted_tokens_list

def frequency_rank(data, input_type, condition=None):
    if condition== 'bigram':
        return pd.DataFrame(list(sort_dict(create_freq_dict(bigrams(data, input_type)))), columns = ['TA_Bigrams', 'Frequency'])
    elif not condition and input_type == 'tiabs': 
        return pd.DataFrame(list(sort_dict(create_freq_dict(unigram(data, input_type)))), columns = ['TA_Unigrams', 'Frequency'])
    else:
        frq_dict, doc_dict = unigram(data, input_type)
        frq_dict = pd.DataFrame(list(sort_dict(frq_dict)), columns = ['MeSH', 'Frequency'])
        
        doc_df = pd.DataFrame([(key, set(value)) for key, value in list(doc_dict.items())], columns = ['MeSH', 'Articles'])
        frq_df = frq_dict.merge(doc_df)
        print(frq_df.head(3))
        return frq_df
          
    
    

