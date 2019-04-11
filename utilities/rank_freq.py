# -*- coding: utf-8 -*-
"""
Created on Wed Oct 03 13:38:34 2018

@author: raylite
"""
import pandas as pd
import numpy as np
from collections import Counter
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#from stopwords import bigram
from nltk.util import ngrams
import SemMedDB.common_terms as ct




def unigram(data, field):
    terms = ct.commonTerminologies()
    common_terms = terms.common_terms    
    stoplist = set(stopwords.words('english') + common_terms + list(string.punctuation))
    
    if field == 'mesh':
        
        tokens = data['MeSH'].str.split(',').tolist()
        tokens = [mesh.lower() for toklist in tokens for mesh in toklist if mesh.lower() not in stoplist]
        
    elif field == 'tiabsmesh':
        df = pd.concat([data['Title'], data['Abstract'],
                        data['MeSH']])
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
    sorted_tokens_list = [(key, value) for key, value in list(tokens_dict.items()) if value >= round(mean)]
    sorted_tokens_list.sort(reverse = True, key = sortKey)
    return sorted_tokens_list

def frequency_rank(data, input_type, condition=None):
    if condition== 'bigram':
        return pd.DataFrame(list(sort_dict(create_freq_dict(bigrams(data, input_type)))), columns = ['TAM_Bigrams', 'Frequency'])
    elif not condition and input_type == 'tiabsmesh': 
        return pd.DataFrame(list(sort_dict(create_freq_dict(unigram(data, input_type)))), columns = ['TAM_Unigrams', 'Frequency'])
    else:
        return pd.DataFrame(list(sort_dict(create_freq_dict(unigram(data, input_type)))), columns = ['MeSH', 'Frequency'])
        
    
    

# =============================================================================
# def save_result(sorted_tokens):
#     tokens_df = pd.DataFrame(list(sorted_tokens), columns = ['Frequency', 'Terms'])
#     tokens_df.to_csv('wordfrquency.csv', encoding = 'utf-8', index = False)
# =============================================================================
    
    
    
# =============================================================================
# def termscloud(tokenTuples):
#     wordcloud = WordCloud().generate_from_frequencies(tokenTuples)
#     
#     plt.figure()
#     plt.imshow(wordcloud, interpolation = 'bilinear')
#     plt.axis('off')
#     plt.show()
# 
# =============================================================================
#read csv file or db records into df

#citations = pd.read_csv('citation_info.csv', index_col = False, encoding = 'utf-8')
    



