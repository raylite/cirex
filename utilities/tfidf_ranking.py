#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 16:45:02 2018

@author: kazeem
"""
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.text import TextCollection
from nltk.util import ngrams
import pandas as pd
import string
import re
import SemMedDB.common_terms as ct#commonTerminologies
"""

"""

def tokenize(doc, input_type = None):
    terms = ct.commonTerminologies()
    common_terms = terms.common_terms#local class defining frequent terms
    stop_words = set(stopwords.words('english') + common_terms + list(string.punctuation))
    #replace special characters with space
    #doc = doc.lower()
    if input_type == 'mesh':
        tokens = doc.split(',')
        for token in tokens:
            if token in string.punctuation or token.isdigit() or token.lower() in stop_words or len(token) <= 2:
                continue
            yield token.lower()
    elif input_type == 'predicate':
        pattern = re.compile("^\s+|\s*,\s*|\s+$")
        grams_tokenizer = [grams.lower() for grams in pattern.split(doc) if not grams.lower() in stop_words]
        for predicate in grams_tokenizer:
            yield predicate
    else:
        for token in word_tokenize(doc):
            if token in string.punctuation or token.isdigit() or token.lower() in stop_words or len(token) <= 2:
                continue
            yield token.lower()

def bigrams(doc_tokens, n=2):
    bigrams = ngrams(doc_tokens, n)
    for grams in bigrams:
        yield ' '.join(grams)

def vectorize(corpus, unigram = True, input_type = None):
    if not unigram and input_type != 'mesh':
        corpus = [list(bigrams(tokenize(doc))) for doc in corpus]
        #tfidf = TfidfVectorizer(ngram_range=(2,2), tokenizer=tokenize,max_df=0.9, 
                           #min_df=2)
    elif not unigram and input_type == 'mesh':
        corpus = [list(tokenize(doc, 'mesh')) for doc in corpus]
    else:
        corpus = [list(tokenize(doc, 'predicate')) for doc in corpus] #predicates
        
    
    texts  = TextCollection(corpus) 
    
    for doc in corpus:
        yield{
                term: texts.tf_idf(term, doc)
                for term in doc
            }
        
def compute_tfidf(corpus, input_type = None, unigram = True, unique = False):
    temp_list = []
    if input_type == 'mesh':
        corpus = corpus['MeSH']
    elif input_type == 'tiabsmesh':
        corpus = corpus['MeSH'] + corpus['Title'] + corpus['Abstract']
    else:
        corpus = corpus
        
    for item in vectorize(corpus, unigram, input_type):
        temp_list.append(item)
    #temp_list = vectorize(corpus)
    
    corpus_df = pd.DataFrame(temp_list)
    if input_type == 'mesh':
        corpus_df = pd.DataFrame(list(corpus_df.sum(axis=0).items()), 
                             columns = ['MeSH_tf', 'Tf-idf score']).sort_values(by=['Tf-idf score'], ascending=False).reset_index(drop=True)
    elif input_type == 'tiabsmesh' and unigram:
        corpus_df = pd.DataFrame(list(corpus_df.sum(axis=0).items()), 
                             columns = ['TAM_tf', 'Tf-idf score']).sort_values(by=['Tf-idf score'], ascending=False).reset_index(drop=True)
    elif input_type == 'tiabsmesh' and not unigram:
        corpus_df = pd.DataFrame(list(corpus_df.sum(axis=0).items()), 
                             columns = ['Bi_TAM_tf', 'Tf-idf score']).sort_values(by=['Tf-idf score'], ascending=False).reset_index(drop=True)
    elif input_type == 'predicate' and unique:
        corpus_df = pd.DataFrame(list(corpus_df.sum(axis=0).items()), 
                             columns = ['U_Pred_tf', 'Tf-idf score']).sort_values(by=['Tf-idf score'], ascending=False).reset_index(drop=True)
    elif input_type == 'predicate' and not unique:
        corpus_df = pd.DataFrame(list(corpus_df.sum(axis=0).items()), 
                             columns = ['Nu_Pred_tf', 'Tf-idf score']).sort_values(by=['Tf-idf score'], ascending=False).reset_index(drop=True)
    
    return corpus_df