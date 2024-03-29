
from cirex.main import bp
from cirex import db
from flask import flash, request, redirect, render_template, url_for, current_app, send_file
import pandas as pd
from io import BytesIO
from utilities import pubmed_downloader, rank_freq, tfidf_ranking
from utilities.SemMedDB import fishers_ranking as fr
from cirex.main.forms import retrieval_form, new_search_form, processing_form, exisitng_search_form
from cirex.models import Search, Article, Database, Result


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@bp.route('/')
def index():
     upload_form = new_search_form()   
     retrieve_form = exisitng_search_form()
     return render_template("index.html", form1 = upload_form, form2 = retrieve_form)


@bp.route('/upload', methods=['POST'])
def upload():
    upload_form = new_search_form()   
    retrieve_form = exisitng_search_form()
    
    if upload_form.validate_on_submit():  
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename =='':
            flash ('No file selected')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            searchinfo = Search(name= upload_form.search_name.data, citation_list = file.read())
            
            db.session.add(searchinfo)
            db.session.commit()
            return redirect(url_for('main.file_view', search_name = searchinfo.name, _external=True))
    
    return render_template("index.html", form1 = upload_form, form2 = retrieve_form)

@bp.route('/retrieve', methods=['POST'])
def retrieve():
    upload_form = new_search_form()   
    retrieve_form = exisitng_search_form()
    
    if retrieve_form.validate_on_submit():
        #load from database
        search = Search.query.filter_by(name = retrieve_form.search_name.data).first()
        return display_results("{}_{}".format(search.name, 'result'))
    return render_template("index.html", form1 = upload_form, form2 = retrieve_form)

@bp.route('/upload_view/<search_name>', methods=['GET', 'POST'])
def file_view(search_name):
        search = Search.query.filter_by(name = search_name).first_or_404()
        citation = search.citation_list.split("\r\n")
        citations = [n for n in citation if n.isdigit()]     
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
            try:
                db.session.bulk_save_objects(articles_list)
                db.session.commit()
            except:
                db.session.rollback()
                raise
            return redirect(url_for('main.retrieved_citations', search_name = search.name))
        return render_template('record-view.html', form = form, records = len(citations), citation_records= citations_list)
            
    
@bp.route('/citations_overview/<search_name>', methods = ['GET', 'POST'])
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
        mesh_terms = rank_freq.frequency_rank(pd.DataFrame(articles), 'mesh')##mesh frequency
        tiabs_terms = rank_freq.frequency_rank(pd.DataFrame(articles), 'tiabs')#tiabs unigram frequency
        tiabs_bigrams = rank_freq.frequency_rank(pd.DataFrame(articles), 'tiabs', 'bigram')#tiabs bigram frequency
        tfidf_bigram_mesh = tfidf_ranking.compute_tfidf(pd.DataFrame(articles), input_type = 'mesh')#mesh tfidf
        tfidf_uni_tiabs = tfidf_ranking.compute_tfidf(pd.DataFrame(articles), input_type = 'tiabs', condition = 'unigram')
        tfidf_bigram_tiabs = tfidf_ranking.compute_tfidf(pd.DataFrame(articles), input_type = 'tiabs', condition = 'bigram')
        
        ##deal with predicates table data
        pmids = pd.to_numeric(pd.DataFrame(articles)['PMID'])
        unique_fishers_rank, unique_chi_rank, multi_fishers_rank, multi_chi_rank, multi_tfidf, unique_tfidf  = fr.analyse_semmed_predicates(pmids)
    
        result = Result(name = '{}_{}'.format(search.name,'result'), search_id = search.id, 
                        freq_mesh_terms = mesh_terms.to_json(orient = 'records'),
                        tfidf_mesh_terms = tfidf_bigram_mesh.to_json(orient = 'records'),
                        freq_tiabs_uni_terms = tiabs_terms.to_json(orient = 'records'),
                        freq_tiabs_bi_terms = tiabs_bigrams.to_json(orient = 'records'),
                        tfidf_tiabs_uni_terms = tfidf_uni_tiabs.to_json(orient = 'records'),
                        tfidf_tiabs_bi_terms = tfidf_bigram_tiabs.to_json(orient = 'records'),
                        tfidf_uniquecount_preds = unique_tfidf.to_json(orient = 'records'),
                        tfidf_multicount_preds = multi_tfidf.to_json(orient = 'records'),
                        fishers_uniquecount_preds = unique_fishers_rank.to_json(orient = 'records'),
                        fishers_multicount_preds = multi_fishers_rank.to_json(orient = 'records'),
                        chi_uniquecount_preds = unique_chi_rank.to_json(orient = 'records'),
                        chi_multicount_preds = multi_chi_rank.to_json(orient = 'records')
                        )
        db.session.add(result)
        db.session.commit()
        return redirect(url_for('main.display_results', results = result.name))
    return render_template('retrieval.html', form = process_form, 
                           data = pd.DataFrame(articles).to_html())


@bp.route('/ranked_terms/<results>')
def display_results(results):
    result = Result.query.filter_by(name = results).first()
    freq_terms = pd.read_json(result.freq_mesh_terms, orient = 'records')
    tiabs_terms = pd.read_json(result.freq_tiabs_uni_terms, orient = 'records')
    tiabs_bi = pd.read_json(result.freq_tiabs_bi_terms, orient = 'records')
    tf_bi_mesh = pd.read_json(result.tfidf_mesh_terms, orient = 'records')
    tf_uni_tiabs = pd.read_json(result.tfidf_tiabs_uni_terms, orient = 'records')
    tf_bi_tiabs = pd.read_json(result.tfidf_tiabs_bi_terms, orient = 'records')
    tf_bi_preds = pd.read_json(result.tfidf_multicount_preds, orient = 'records')
    tf_unique_preds = pd.read_json(result.tfidf_uniquecount_preds, orient = 'records')
    f_unique_preds = pd.read_json(result.fishers_uniquecount_preds, orient = 'records')
    f_bi_preds = pd.read_json(result.fishers_multicount_preds, orient = 'records')  
    chi_unique_preds = pd.read_json(result.chi_uniquecount_preds, orient = 'records')
    chi_bi_preds = pd.read_json(result.chi_multicount_preds, orient = 'records')
    
    return render_template('result.html', 
                           unigrams = pd.DataFrame(freq_terms[['MeSH']]).to_html(), #reduction handled in the code
                           tiabs_uni = pd.DataFrame(tiabs_terms[['TA_Unigrams']]).to_html(),
                           tiabs_bi = pd.DataFrame(tiabs_bi[['TA_Bigrams']]).to_html(),
                           tf_mesh = pd.DataFrame(tf_bi_mesh[['MeSH_tf']][tf_bi_mesh['Tf-idf score'].gt(0.05)]).to_html(),
                           tf_uni_tiabs = pd.DataFrame(tf_uni_tiabs[['TA_tf']][tf_uni_tiabs['Tf-idf score'].gt(0.05)]).to_html(),
                           tf_bi_tiabs = pd.DataFrame(tf_bi_tiabs[['Bi_TA_tf']][tf_bi_tiabs['Tf-idf score'].gt(0.05)]).to_html(),
                           tf_bi_preds = pd.DataFrame(tf_bi_preds['Nu_Pred_tf'][tf_bi_preds['Tf-idf score'].gt(0.02)]).to_html(),
                           tf_unique_preds = pd.DataFrame(tf_unique_preds[['U_Pred_tf']][tf_unique_preds['Tf-idf score'].gt(0.02)]).to_html(),
                           f_unique_preds = pd.DataFrame(f_unique_preds[['Un_F_Predicates']]).to_html(),
                           f_bi_preds = pd.DataFrame(f_bi_preds[['Nu_F_Predicates']]).to_html(),
                           chi_unique_preds = pd.DataFrame(chi_unique_preds[['Un_Chi2_Predicates']]).to_html(),
                           chi_bi_preds = pd.DataFrame(chi_bi_preds[['Nu_Chi2_Predicates']]).to_html(), result = result
                           )

  
@bp.route('/download/<results>', methods=['GET'])
def download(results):
    result = Result.query.filter_by(name = results).first()
    freq_terms = pd.read_json(result.freq_mesh_terms, orient = 'records')[['MeSH', 'Frequency', 'Articles']]
    tiabs_terms = pd.read_json(result.freq_tiabs_uni_terms, orient = 'records')[['TA_Unigrams']]
    tiabs_bi = pd.read_json(result.freq_tiabs_bi_terms, orient = 'records')[['TA_Bigrams']]
    tf_bi_mesh = pd.read_json(result.tfidf_mesh_terms, orient = 'records')[['MeSH_tf']]
    tf_uni_tiabs = pd.read_json(result.tfidf_tiabs_uni_terms, orient = 'records')[['TA_tf']]
    tf_bi_tiabs = pd.read_json(result.tfidf_tiabs_bi_terms, orient = 'records')[['Bi_TA_tf']]
    tf_bi_preds = pd.read_json(result.tfidf_multicount_preds, orient = 'records')[['Nu_Pred_tf']]
    tf_unique_preds = pd.read_json(result.tfidf_uniquecount_preds, orient = 'records')[['U_Pred_tf']]
    f_unique_preds = pd.read_json(result.fishers_uniquecount_preds, orient = 'records')[['Un_F_Predicates', 'Docs_Count']]
    f_bi_preds = pd.read_json(result.fishers_multicount_preds, orient = 'records')[['Nu_F_Predicates']]  
    chi_unique_preds = pd.read_json(result.chi_uniquecount_preds, orient = 'records')[['Un_Chi2_Predicates']]
    chi_bi_preds = pd.read_json(result.chi_multicount_preds, orient = 'records')[['Nu_Chi2_Predicates']]
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        freq_terms.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'MeSH frequency')
        tiabs_terms.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'TiAbs unigram frequency')
        tiabs_bi.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'TiAbs bigram frequency')
        tf_bi_mesh.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'MeSH tfidf rank')
        tf_uni_tiabs.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'TiAbs unigram tfidf')
        tf_bi_tiabs.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'TiAbs bigram tfidf')
        tf_bi_preds.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'Preds multicount tfidf')
        tf_unique_preds.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'Preds unicount tfidf')
        f_unique_preds.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'Preds unicount Fishers')
        f_bi_preds.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'Preds multicount Fishers')
        chi_unique_preds.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'Preds unicount Chi')
        chi_bi_preds.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'Preds multicount Chi')
    
        workbook = writer.book
        worksheet = writer.sheets['MeSH frequency']
        worksheet = writer.sheets['TiAbs unigram frequency']
        worksheet = writer.sheets['TiAbs bigram frequency']
        worksheet = writer.sheets['MeSH tfidf rank']
        worksheet = writer.sheets['TiAbs unigram tfidf']
        worksheet = writer.sheets['TiAbs bigram tfidf']
        worksheet = writer.sheets['Preds multicount tfidf']
        worksheet = writer.sheets['Preds unicount tfidf']
        worksheet = writer.sheets['Preds unicount Fishers']
        worksheet = writer.sheets['Preds multicount Fishers']
        worksheet = writer.sheets['Preds unicount Chi']
        worksheet = writer.sheets['Preds multicount Chi']
        
        format = workbook.add_format()
        format.set_bg_color('#eeeeee')
        worksheet.set_column(1, 2, 40)
        
    output.seek(0)
    return send_file(output, attachment_filename=f"{results}.xlsx", as_attachment=True)
    
    
    
@bp.route('/overview_download/<results>', methods=['GET'])
def download_records(results):
    search = Search.query.filter_by(name = results.split('_')[0]).first()
    records = Article.query.filter_by(search_id = search.id).all()#takes result name extraxt the first part to search database
    articles = []
    
    for record in records:
        articles.append({"Abstract": record.abstract,
                   "PMID": record.pmid,
                   "MeSH": record.mesh,
                   "Year": record.date,
                   "Authors": record.authors,
                   "Journal": record.journal,
                   "Title": record.title,
                   "DOI": record.doi,
                   "PII": record.pii,
                   "MeSH_Qualifier": record.mesh_qualifier,
                   "Database": ', '.join([publisher.name for publisher in record.databases])
                  })
        
    articles_df = pd.DataFrame(articles)    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        articles_df.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = 'Records overview')
    
        workbook = writer.book
        worksheet = writer.sheets['Records overview']
        
        format = workbook.add_format()
        format.set_bg_color('#eeeeee')
        worksheet.set_column(1, 2, 40)
        
    output.seek(0)
    return send_file(output, attachment_filename=f"{search.name}_overview.xlsx", as_attachment=True)   
    
    
    
    
    
    