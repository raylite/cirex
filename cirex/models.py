 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 12:24:40 2018

@author: kazeem
"""

from cirex import db
from sqlalchemy.dialects.mysql import LONGTEXT

class Search(db.Model):    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True, unique = True)
    citation_list = db.Column(LONGTEXT())
    search_string = db.Column(db.String(500), index = True, unique = True)
    citations = db.relationship('Article', backref = 'base_search', lazy = 'dynamic')
    results = db.relationship('Result', backref = 'search')
    
    def __repr__(self):
        return '<Search Identifier: {}>'.format(self.name)


class Database(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True)
    articles = db.relationship('Article', secondary='article_databases', lazy = 'subquery',
                               backref = db.backref('databases', lazy = True))
    
    def __repr__(self):
        return '<Database: {}>'.format(self.name)
    
    
class Article(db.Model):   
    id = db.Column(db.Integer, primary_key = True)
    pmid = db.Column(db.Integer, index = True)
    mesh = db.Column(db.Text)
    doi = db.Column(db.String(128), index = True)
    pii = db.Column(db.String(128), index = True)
    abstract = db.Column(LONGTEXT(charset='utf8mb4'))
    title = db.Column(LONGTEXT())
    date = db.Column(db.String(16))
    volume = db.Column(db.Integer)
    authors = db.Column(LONGTEXT(charset='utf8mb4'))
    journal = db.Column(db.String(128), index = True)
    mesh_qualifier = db.Column(LONGTEXT())
    #databases = db.relationship('Database', secondary='article_database')
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    
    
    def __repr__(self):
        return '<Article: {}>'.format(self.title)
    

article_databases = db.Table('article_databases',
                   db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key = True),
                   db.Column('database_id', db.Integer, db.ForeignKey('database.id'), primary_key = True))
    
    
class Result(db.Model):   
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32))
    freq_mesh_bi_terms = db.Column(LONGTEXT())
    tfidf_mesh_uni_terms = db.Column(LONGTEXT())
    tfidf_mesh_bi_terms = db.Column(LONGTEXT())
    freq_tiabs_uni_terms = db.Column(LONGTEXT())
    freq_tiabs_bi_terms = db.Column(LONGTEXT())
    tfidf_tiabs_uni_terms = db.Column(LONGTEXT())
    tfidf_tiabs_bi_terms = db.Column(LONGTEXT())
    tfidf_preds_uni = db.Column(LONGTEXT())
    tfidf_preds_multi = db.Column(LONGTEXT())
    fishers_unique_preds = db.Column(LONGTEXT())
    fishers_multi_preds = db.Column(LONGTEXT())
    chi_preds_unique = db.Column(LONGTEXT())
    chi_preds_bi = db.Column(LONGTEXT())
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))