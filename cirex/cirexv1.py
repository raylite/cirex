# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 11:52:08 2018

@author: raylite
"""
import pandas as pd

from pubmed_downloader import PMID_Search

##imports list


################

#STEP 1: Read a txt or csv file. Use iteator (Use readlines if possible)
def load_n_citations(filename, n=1):
    try:
        with open(filename) as f:#use picker to automatically get filename
            while  True:
                batch_citation = ''.join(f.readline() for i in range(n))
                if batch_citation:
                    yield [batch_citation.replace('\n', ',')]
                else:
                    
                    break
    except:
        print ("Unable to open file")
    



##STEP 2: Source a more structured information from crossref


##STEP 3: Download from databases
        
        

if __name__=='__main__':
    ###process file record
    trees = ''
    citation_list = []
    filename = 'citation.txt'
    for index, chunk in enumerate(load_n_citations(filename,5)):
        citation_record = PMID_Search(chunk) #returns a dataframe
        citation_list.append(citation_record)
    citation_df = pd.concat(citation_list, ignore_index = True)
    print (citation_df) #to store