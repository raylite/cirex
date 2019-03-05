
from cirex import app
from cirex import db

import os
from flask import flash, request, redirect, render_template, url_for
#from werkzeug.utils import secure_filename

import pandas as pd
#import json

from utilities import pubmed_downloader, rank_freq, tfidf_ranking
from utilities.SemMedDB import fishers_ranking as fr
from .forms import retrieval_form, new_search_form, processing_form, exisitng_search_form
from .models import Search, Article, Database, Result


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route('/')
@app.route('/index')
def index():
     upload_form = new_search_form()   
     retrieve_form = exisitng_search_form()
     return render_template("upload.html", form1 = upload_form, form2 = retrieve_form)



@app.route('/upload', methods=['POST', 'GET'])
def upload():
    upload_form = new_search_form()   
    retrieve_form = exisitng_search_form()
    
    if request.method == 'POST' and upload_form.validate_on_submit():  
        if not os.path.isdir(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename =='':
            flash ('No file selected')
            return redirect(request.url)
        

        if file and allowed_file(file.filename):
            searchinfo = Search(name= upload_form.search_id.data, citation_list = file.read())
            db.session.add(searchinfo)
            db.session.commit()
            return redirect(url_for('uploaded_file', search_name = searchinfo.name))
    
    elif request.method == 'GET' and retrieve_form.validate_on_submit():
        #load from database
        search = Search.query.filter_by(name = retrieve_form.search_name.data).first()
        result = Result.query.filter_by(search_id = search.id)
        redirect(url_for('result.html', result = result.id or "Yet to build result"))
    return render_template("upload.html", form1 = upload_form, form2 = retrieve_form)

@app.route('/upload_view/<search_name>', methods=['GET', 'POST'])
def uploaded_file(search_name):
        search = Search.query.filter_by(name = search_name).first_or_404()
        citations = search.citation_list.split("\r\n")
        
        citations_list = []
         
        
        for record in range(len(citations)):
            citations_list.append(citations[record].split(" "))
            
        articles_list = []
        
        form = retrieval_form()
        
        if form.validate_on_submit():
            citations_record = pubmed_downloader.PMID_Search(citations)
            
            for record in citations_record.itertuples():
                database = Database.query.filter_by(name = record.db).first()
                if database is None:
                    database = Database(name = record.db)
                    db.session.add(database)
                    
                                
                article = Article(search_id = search.id,
                                  pmid = record.PMID,
                                  mesh = record.MeSH,
                                  title = record.Title,
                                  abstract = record.Abstract,
                                  date = record.Year,
                                  authors = record.Authors,
                                  journal = record.Journal,
                                  doi = record.DOI,
                                  pii = record.PII,
                                  mesh_qualifier = record.MeSH_Qualifier
                                  )
                
                article.databases.append(database)
                
            articles_list.append(article)
            db.session.add_all(articles_list)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            return redirect(url_for('retrieved_citations', search_name = search.name))
        return render_template('record-view.html', form = form, records = len(citations), citation_records= citations_list)
            
    
@app.route('/citations_overview/<search_name>', methods = ['GET', 'POST'])
def retrieved_citations(search_name):
    articles = []
    search = Search.query.filter_by(name = search_name).first()
    article_records = Article.query.filter_by(search_id = search.id).all()
    for record in article_records:
        article = {"Abstract": record.abstract,
                   "PMID": record.pmid,
                   "MeSH": record.mesh,
                   "Year": record.date,
                   "Authors": record.authors,
                   "Journal": record.journal,
                   "Title": record.title,
                   "DOI": record.doi,
                   "PII": record.pii,
                   "MeSH_Qualifier": record.mesh_qualifier,
                   "Publisher": ', '.join([publisher.name for publisher in record.databases])
                  }
        articles.append(article)
        
    process_form = processing_form()
    if process_form.validate_on_submit():
        mesh_terms = pd.DataFrame(list(rank_freq.sort_dict(rank_freq.create_freq_dict(rank_freq.unigram(pd.DataFrame(articles), 'mesh')))), 
                             columns = ['MeSH', 'Frequency'])##mesh frequency
        tiabs_terms = pd.DataFrame(list(rank_freq.sort_dict(rank_freq.create_freq_dict(rank_freq.unigram(pd.DataFrame(articles), 'tiabsmesh')))), 
                             columns = ['TAM_Unigrams', 'Frequency'])#tiabs unigram frequency
        tiabs_bigrams = pd.DataFrame(list(rank_freq.sort_dict(rank_freq.create_freq_dict(rank_freq.bigrams(pd.DataFrame(articles), 'tiabsmesh')))), 
                             columns = ['TAM_Bigrams', 'Frequency'])#tiabs bigram frequency
        tfidf_bigram_mesh = tfidf_ranking.compute_tfidf(pd.DataFrame(articles), 'mesh', unigram = False)#mesh tfidf
        tfidf_uni_tiabs = tfidf_ranking.compute_tfidf(pd.DataFrame(articles), 'tiabsmesh')
        tfidf_bigram_tiabs = tfidf_ranking.compute_tfidf(pd.DataFrame(articles), 'tiabsmesh', unigram = False)
        
        ##deal with predicates table data
        pmids = pd.DataFrame(articles)['PMID']
        unique_fishers_rank, unique_chi_rank, multi_fishers_rank, multi_chi_rank, unique_tfidf, multi_tfidf = fr.analyse_semmed_predicates(pmids)
        #unique_multi_fishers_rank, unique_gram_chi_rank = fr.retrieve_predicates_data(pmids, unique = True)
            
        result = Result(name = '{}_{}'.format(search.name,'result'), search_id = search.id, 
                        freq_mesh_uni_terms = mesh_terms.to_json(orient = 'records'),
                        freq_tiabs_bi_terms = tiabs_bigrams.to_json(orient = 'records'),
                        freq_tiabs_uni_terms = tiabs_terms.to_json(orient = 'records'),
                        tfidf_mesh_bi_terms = tfidf_bigram_mesh.to_json(orient = 'records'),
                        tfidf_tiabs_uni_terms = tfidf_uni_tiabs.to_json(orient = 'records'),
                        tfidf_tiabs_bi_terms = tfidf_bigram_tiabs.to_json(orient = 'records'),
                        tfidf_preds_multi = multi_tfidf.to_json(orient = 'records'),
                        tfidf_preds_unique = unique_tfidf.to_json(orient = 'records'),
                        fishers_unique_preds = unique_fishers_rank.to_json(orient = 'records'),
                        fishers_multi_preds = multi_fishers_rank.to_json(orient = 'records'),
                        chi_preds_unique = unique_chi_rank.to_json(orient = 'records'),
                        chi_preds_bi = multi_chi_rank.to_json(orient = 'records')
                        )
        db.session.add(result)
        db.session.commit()
        return redirect(url_for('display_results', results = result.name))
    return render_template('retrieval.html', form = process_form, 
                           data = pd.DataFrame(articles).to_html())


@app.route('/ranked_terms/<results>')
def display_results(results):
    result = Result.query.filter_by(name = results).first()
    freq_terms = pd.read_json(result.freq_mesh_uni_terms, orient = 'records')
    tiabs_terms = pd.read_json(result.freq_tiabs_uni_terms, orient = 'records')
    tiabs_bi = pd.read_json(result.freq_tiabs_bi_terms, orient = 'records')
    tf_bi_mesh = pd.read_json(result.tfidf_mesh_bi_terms, orient = 'records')
    tf_uni_tiabs = pd.read_json(result.tfidf_tiabs_uni_terms, orient = 'records')
    tf_bi_tiabs = pd.read_json(result.tfidf_tiabs_bi_terms, orient = 'records')
    tf_bi_preds = pd.read_json(result.tfidf_preds_multi, orient = 'records')
    tf_unique_preds = pd.read_json(result.tfidf_preds_unique, orient = 'records')
    f_unique_preds = pd.read_json(result.fishers_unique_preds, orient = 'records')
    f_bi_preds = pd.read_json(result.fishers_multi_preds, orient = 'records')
    
    chi_unique_preds = pd.read_json(result.chi_preds_unique, orient = 'records')
    chi_bi_preds = pd.read_json(result.chi_preds_bi, orient = 'records')
    return render_template('result.html', 
                           unigrams = pd.DataFrame(freq_terms['MeSH']).to_html(), 
                           tiabs_uni = pd.DataFrame(tiabs_terms['TAM_Unigrams']).to_html(),
                           tiabs_bi = pd.DataFrame(tiabs_bi['TAM_Bigrams']).to_html(),
                           tf_mesh = pd.DataFrame(tf_bi_mesh['MeSH_tf']).to_html(),
                           tf_uni_tiabs = pd.DataFrame(tf_uni_tiabs['TAM_tf']).to_html(),
                           tf_bi_tiabs = pd.DataFrame(tf_bi_tiabs['Bi_TAM_tf']).to_html(),
                           tf_bi_preds = pd.DataFrame(tf_bi_preds['Nu_Pred_tf']).to_html(),
                           tf_unique_preds = pd.DataFrame(tf_unique_preds['U_Pred_tf']).to_html(),
                           f_unique_preds = pd.DataFrame(f_unique_preds['Un_F_Predicates', 'Docs_count']).to_html(),
                           f_bi_preds = pd.DataFrame(f_bi_preds[['Nu_F_Predicates', 'Docs_count']]).to_html(),
                           chi_unique_preds = pd.DataFrame(chi_unique_preds['Un_Chi2_Predicates']).to_html(),
                           chi_bi_preds = pd.DataFrame(chi_bi_preds['Nu_Chi2_Predicates']).to_html()
                           )