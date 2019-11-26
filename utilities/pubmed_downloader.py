# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 11:29:10 2018

@author: raylite
"""

from Bio import Entrez
import pandas as pd
from urllib.error import HTTPError
import time
#import xml.etree.ElementTree as ET
from lxml import etree as ET

API_KEY = 'a2e2a3e33502aa03aa40735fb24c80de9008'
tool = "CiREx"


def PMID_Search(id_list):
    Entrez.email = "b.k.olorisade@bristol.ac.uk"
    Entrez.api_key = API_KEY
    Entrez.tool = tool
    
    search_results = Entrez.read(Entrez.epost("pubmed", id=",".join(id_list)))
    webenv = search_results["WebEnv"]
    query_key = search_results["QueryKey"]
    count = len(id_list)
    batch_size = 100
    abstract = None
    all_docs = []
    mesh_head = None
    mesh_qual = ""
    doi = None
    
    
    for start in range(0, count, batch_size):
        end = min(count, start+batch_size)
        print("Going to download record {} to {}".format(start+1, end))
        attempt = 0
        success = False
        while not success and attempt < 3:
            try:
                fetch_handle = Entrez.efetch(db="pubmed",
                                             rettype="abstract", retmode="xml",
                                             retstart=start, retmax=batch_size,
                                             webenv=webenv, query_key=query_key)
                #try rettype=abstract, retmode = text
                success = True
            except HTTPError as err:
                if 500 <= err.code <= 599:
                    print("Received error from server %s" % err)
                    print("Attempt %i of 3" % attempt)
                    time.sleep(15)
                    attempt += 1
                else:
                    raise
            else:
                data = fetch_handle.read()
                fetch_handle.close()
                tree = ET.XML(data)
        
        for doc in tree:
            authors = []
            
            PMID = doc.xpath(".//MedlineCitation/PMID[@Version='1']/text()") 
            title = doc.xpath(".//ArticleTitle/text()")
            year = doc.xpath(".//PubDate/Year/text()")
            month = doc.xpath(".//PubDate/Month/text()")
            journal = doc.xpath(".//Journal/Title/text()")
            doi = doc.xpath(".//ArticleId[@IdType='doi']/text()")#.text#select doi, pii and pubmend by IdType attribute
            pii = doc.xpath(".//ArticleId[@IdType='pii']/text()")
                
            abstract = doc.xpath(".//AbstractText/text()")
            mesh_head = doc.xpath(".//MeshHeading/DescriptorName/text()")
            mesh_qual = doc.xpath(".//MeshHeading/QualifierName/text()")#mesh qualifier
            
            authorslastnames = doc.xpath(".//Author/LastName/text()")
            authorsfirstnames = doc.xpath(".//Author/ForeName/text()")#zip both, extract and append
            
# =============================================================================
            for last, first in zip(authorslastnames, authorsfirstnames):
                if last is not None and first is not None:
                    authors.append(" ".join([last, first]))
# =============================================================================
                    
            docs = {
                    "PMID": PMID or None,
                    "Title": ' '.join(title) or None,
                    "Abstract": ' '.join(abstract) or None,
                    "MeSH": ', '.join(mesh_head),
                    "db": "PubMed",
                    "MeSH_Qualifier": ' '.join(mesh_qual) or None,
                    "DOI": ' '.join(doi) or None,
                    "PII": ' '.join(pii) or None,     
                    "Year": '-'.join(month + year) or None,
                    "Journal": ' '.join(journal) or None,
                    "Authors": ', '.join([" ".join([last, first]) for last, first in zip(authorslastnames, authorsfirstnames)]) or None
                    }
            all_docs.append(docs) 
        
    return pd.DataFrame(all_docs)
