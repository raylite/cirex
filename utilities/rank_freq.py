# -*- coding: utf-8 -*-
"""
Created on Wed Oct 03 13:38:34 2018

@author: raylite
"""
import pandas as pd
from collections import Counter
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#from stopwords import bigram
from nltk.util import ngrams
import SemMedDB.common_terms as ct




def unigram(index_information, field):
    terms = ct.commonTerminologies()
    common_terms = terms.common_terms    
    stoplist = set(stopwords.words('english') + common_terms + list(string.punctuation))
    
    if field == 'mesh':
        
        tokens = index_information['MeSH'].str.split(',').tolist()
        tokens = [mesh.lower() for toklist in tokens for mesh in toklist if mesh.lower() not in stoplist]
        
    elif field == 'tiabsmesh':
        df = pd.concat([index_information['Title'], index_information['Abstract'],
                        index_information['MeSH']])
        tokens = word_tokenize(df.str.cat(sep = ' ').lower())
   
        translator = str.maketrans('', '', string.punctuation+string.digits)#python 3
        tokens = [token.translate(translator) for token in tokens]
        
    tokens = [token for token in tokens if token and token not in stoplist and len(token) > 3] #removes any None element
    
    return tokens

def bigrams(index_information, field, n=2):
    bigrams = ngrams(unigram(index_information, field), n)
    return [' '.join(grams) for grams in bigrams] 

def create_freq_dict(tokens_list):
    frequency_dict = Counter(tokens_list)
    
    return frequency_dict

def sortKey(tokenslist):
    return tokenslist[1]


def sort_dict(tokens_dict):
    sorted_tokens_list = [(key, value) for key, value in list(tokens_dict.items())]# if value > 2]
    sorted_tokens_list.sort(reverse = True, key = sortKey)
    return sorted_tokens_list



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
    



