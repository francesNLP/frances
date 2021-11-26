from flask import Flask, render_template, request, jsonify, session
from .flask_app import app
import requests
import traceback
from .sparql_queries import *
from flask_paginate import Pagination, get_page_parameter
import itertools
from itertools import islice
from sklearn.metrics.pairwise import cosine_similarity
from .utils import calculating_similarity_text, get_topic_name, load_data

import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from bertopic import BERTopic

########
input_path_embed="/Users/rosafilgueira/HW-Work/NLS-Fellowship/work/frances/web-app/models/all-mpnet-base-v2"
input_path="/Users/rosafilgueira/HW-Work/NLS-Fellowship/work/frances/web-app/models/"

text_embeddings = np.load('/Users/rosafilgueira/HW-Work/NLS-Fellowship/work/frances/web-app/models/all-mpnet-base-v2/embeddings_1ed.npy')
topic_model = BERTopic.load("/Users/rosafilgueira/HW-Work/NLS-Fellowship/work/frances/web-app/models/all-mpnet-base-v2/BerTopic_Model_1ed") 

similarities=load_data(input_path_embed, 'similarities_1ed.txt')
similarities_sorted=load_data(input_path_embed, 'similarities_sorted_1ed.txt')
documents=load_data(input_path, 'documents_1ed.txt')
terms_info=load_data(input_path, 'terms_info_1ed.txt')
uris=load_data(input_path, 'uris_1ed.txt')
topics=load_data(input_path_embed, 'topics_1ed.txt')
topics_name=load_data(input_path_embed, 'topics_names_1ed.txt')
topics_names=load_data(input_path_embed, 'topics_names_1ed.txt')
summary_1771=load_data(input_path,'topics_summary_1771.txt') 
sentiment_terms=load_data(input_path,'sentiment_documents_1ed.txt') 

#model = SentenceTransformer('bert-base-nli-mean-tokens')
#model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer('all-mpnet-base-v2')


######

@app.route("/", methods=["GET"])
def home_page():
    return render_template('home.html')

@app.route("/term_search/<string:termlink>",  methods=['GET', 'POST'])
@app.route("/term_search",  methods=['GET', 'POST'])
def term_search(termlink=None):
    
    headers=["Year", "Edition", "Volume", "Start Page", "End Page", "Term Type", "Definition", "Related Terms", "Topic Modelling", "Sentiment_Score"]
    if request.method == "POST":
        if "search" in request.form:
            term = request.form["search"]
        if not term:
            term = "ABACISCUS"
        term=term.upper()
        session['term'] = term
    
    if termlink!=None:
        term = termlink
        session['term'] = term
    else:
        term=session.get('term')
    if not term:
        term = "ABACISCUS"
    results =get_definition(term)
    topics_vis=[]
    for key, value in results.items():
        index_uri=uris.index(key)
        topic_name = topics_names[index_uri]
        score='%.2f'%sentiment_terms[index_uri][0]['score']
        sentiment = sentiment_terms[index_uri][0]['label']+"_"+score
        if topics[index_uri] not in topics_vis:
            topics_vis.append(topics[index_uri])
        #topic_name = get_topic_name(index_uri, topics, topic_model)
        value.append(topic_name)
        value.append(sentiment)
    if len(topics_vis) >= 1:
        fig1=topic_model.visualize_barchart(topics_vis, n_words=10)
        bar_plot = fig1.to_json() 
    else:
        bar_plot=None
    if len(topics_vis) >= 2:
        fig2=topic_model.visualize_heatmap(topics_vis)
        heatmap_plot = fig2.to_json()
    else:
        heatmap_plot=None
 
    page = int(request.args.get("page", 1))
    page_size=2
    per_page = 2
    offset = (page-1) * per_page
    limit = offset+per_page
    results_for_render=dict(islice(results.items(),offset, limit))
    pagination = Pagination(page=page, total=len(results), per_page=page_size, search=False)
    return render_template("results.html", results=results_for_render,
                                           pagination = pagination, 
                                           headers=headers,
                                           term=term, bar_plot=bar_plot, heatmap_plot=heatmap_plot)
       

@app.route("/eb_details",  methods=['GET', 'POST'])
def eb_details():
    edList=get_editions()
    if 'edition_selection' in request.form and 'volume_selection' in request.form:
        ed_raw=request.form.get('edition_selection')
        vol_raw=request.form.get('volume_selection')
        if vol_raw !="" and ed_raw !="":
            ed_uri="<"+ed_raw+">"
            ed_r=get_editions_details(ed_uri)
            vol_uri="<"+vol_raw+">"
            ed_v=get_volume_details(vol_uri)
            ed_st=get_vol_statistics(vol_uri)
            ed_name=edList[ed_raw]
            vol_name=get_vol_by_vol_uri(vol_uri)
            return render_template('eb_details.html', edList=edList,  ed_r=ed_r, ed_v=ed_v, ed_st=ed_st, ed_name=ed_name, vol_name=vol_name)
        else:
            return render_template('eb_details.html', edList=edList)
    return render_template('eb_details.html', edList=edList)

   

 

@app.route("/vol_details", methods=['GET', 'POST'])
def vol_details():
    if request.method == "POST":
        uri_raw=request.form.get('edition_selection')
        uri="<"+uri_raw+">"
        volList=get_volumes(uri)
        OutputArray = []
        for key, value in sorted(volList.items(), key=lambda item: item[1]):
            outputObj = { 'id':key , 'name': value }
            OutputArray.append(outputObj)
    return jsonify(OutputArray)



@app.route("/visualization_resources", methods=['GET', 'POST'])
def visualization_resources(termlink=None, termtype=None):
    if request.method == "POST":
        if 'resource_uri' in request.form:
            uri_raw=request.form.get('resource_uri').strip().replace("<","").replace(">","")
            if uri_raw == "":
                uri="<https://w3id.org/eb/i/Article/992277653804341_144133901_ABACISCUS_0>"
            else:
                uri="<"+uri_raw+">"
            g_results=describe_resource(uri)
            return render_template('visualization_resources.html', g_results=g_results, uri=uri)
    else:
        termlink  = request.args.get('termlink', None)
        termtype  = request.args.get('termtype', None)
        if termlink!=None:
            if ">" in termlink:
                termlink=termlink.split(">")[0]
            uri="<https://w3id.org/eb/i/"+termtype+"/"+termlink+">"
            g_results=describe_resource(uri)
            return render_template('visualization_resources.html', g_results=g_results, uri=uri)
        else:
            return render_template('visualization_resources.html')

@app.route("/similar_terms", methods=["GET", "POST"])
def similar_terms(termlink=None):
    if request.method == "POST":
        if 'resource_uri' in request.form:
            data_similar=request.form.get('resource_uri')
            if "https://" in data_similar or "w3id" in data_similar:
                uri_raw=data_similar.strip().replace("<","").replace(">","")
            elif data_similar == "":
                uri_raw="https://w3id.org/eb/i/Article/992277653804341_144133901_ABACISCUS_0"
            else:
                uri_raw=""
                results, topics_vis=calculating_similarity_text(data_similar,text_embeddings, model, terms_info, documents,uris, topics_names,topics, sentiment_terms)              
                if len(topics_vis) >= 1:
                    fig1=topic_model.visualize_barchart(topics_vis, n_words=10)
                    bar_plot = fig1.to_json() 
                else:
                    bar_plot=None
                if len(topics_vis) >= 2:
                    fig2=topic_model.visualize_heatmap(topics_vis)
                    heatmap_plot = fig2.to_json()
                else:
                    heatmap_plot=None
            if uri_raw!="":
                uri="<"+uri_raw+">"
                term, definition, enum, year, vnum  =get_document(uri)
                index_uri=uris.index(uri_raw)
                t_name=topics_names[index_uri]
                score='%.2f'%sentiment_terms[index_uri][0]['score']
                t_sentiment = sentiment_terms[index_uri][0]['label']+"_"+score
                results={}
                topics_vis=[]
                for i in range(-2, -12, -1):
                    similar_index=similarities_sorted[index_uri][i]
                    rank=similarities[index_uri][similar_index]
                    score='%.2f'%sentiment_terms[similar_index][0]['score']
                    sentiment = sentiment_terms[similar_index][0]['label']+"_"+score
                    topic_name = topics_names[similar_index]
                    if topics[similar_index] not in topics_vis:
                        topics_vis.append(topics[similar_index])
                    results[uris[similar_index]]=[terms_info[similar_index][1],terms_info[similar_index][2], terms_info[similar_index][4], terms_info[similar_index][0], documents[similar_index], topic_name, rank, sentiment]
                if len(topics_vis) >= 1:
                    fig1=topic_model.visualize_barchart(topics_vis, n_words=10)
                    bar_plot = fig1.to_json()
                else:
                    bar_plot=None
                if len(topics_vis) >= 2:
                    fig2=topic_model.visualize_heatmap(topics_vis)
                    heatmap_plot = fig2.to_json()
                else:
                    heatmap_plot=None
    
            if uri_raw == "":
                return render_template('similar.html', results=results, bar_plot=bar_plot, heatmap_plot=heatmap_plot)
            else:
                return render_template('similar.html', results=results, term=term, definition=definition, uri=uri_raw, enum=enum, year=year, vnum=vnum, t_name=t_name, bar_plot=bar_plot, heatmap_plot=heatmap_plot, t_sentiment=t_sentiment)
    
    termlink  = request.args.get('termlink', None)
    termtype  = request.args.get('termtype', None)
    if termlink!=None:
        if ">" in termlink:
            termlink=termlink.split(">")[0]
        uri="<https://w3id.org/eb/i/"+termtype+"/"+termlink+">"
        term, definition, enum, year, vnum  =get_document(uri)
        uri_raw=uri.replace("<","").replace(">","")
        index_uri=uris.index(uri_raw)
        t_name=topics_names[index_uri]
        score='%.2f'%sentiment_terms[index_uri][0]['score']
        t_sentiment = sentiment_terms[index_uri][0]['label']+"_"+score
        results={}
        topics_vis=[]
        for i in range(-2, -12, -1):
            similar_index=similarities_sorted[index_uri][i]
            rank=similarities[index_uri][similar_index]
            score='%.2f'%sentiment_terms[similar_index][0]['score']
            sentiment = sentiment_terms[similar_index][0]['label']+"_"+score
            topic_name = topics_names[similar_index]
            if topics[similar_index] not in topics_vis:
                topics_vis.append(topics[similar_index])
            results[uris[similar_index]]=[terms_info[similar_index][1],terms_info[similar_index][2], terms_info[similar_index][4], terms_info[similar_index][0], documents[similar_index], topic_name, rank, sentiment]

        if len(topics_vis) >= 1:
            fig1=topic_model.visualize_barchart(topics_vis, n_words=10)
            bar_plot = fig1.to_json() 
        else:
            bar_plot = None
        if len(topics_vis) >= 2:
            fig2=topic_model.visualize_heatmap(topics_vis)
            heatmap_plot = fig2.to_json()
        else:
            heatmap_plot = None
        return render_template('similar.html', results=results, term=term, definition=definition, uri=uri, enum=enum, year=year, vnum=vnum, t_name=t_name, bar_plot=bar_plot, heatmap_plot=heatmap_plot, t_sentiment=t_sentiment)
    return render_template('similar.html')

@app.route("/topic_modelling", methods=["GET", "POST"])
def topic_modelling(topic_name=None):
    if request.method == "POST":
        if 'topic_name' in request.form:
            topic_name=request.form.get('topic_name')
            if topic_name=="":
                topic_name="5_see_dialling_villain_article"
            indices = [i for i, x in enumerate(topics_names) if x == topic_name]
            results={}
            for t_i in indices:
               score='%.2f'%sentiment_terms[t_i][0]['score']
               sentiment = sentiment_terms[t_i][0]['label']+"_"+score
               results[uris[t_i]]=[terms_info[t_i][1],terms_info[t_i][2], terms_info[t_i][4], terms_info[t_i][0], documents[t_i], sentiment]
            num_results=len(indices)
            first_topic=topics[indices[0]]
            fig1=topic_model.visualize_barchart([first_topic], n_words=10)
            bar_plot = fig1.to_json()
            return render_template('topic_modelling.html', topic_name=topic_name, results=results, bar_plot=bar_plot, num_results=num_results) 
    topic_name  = request.args.get('topic_name', None)
    if topic_name!=None:
        indices = [i for i, x in enumerate(topics_names) if x == topic_name]
        results={}
        for t_i in indices:
            score='%.2f'%sentiment_terms[t_i][0]['score']
            sentiment = sentiment_terms[t_i][0]['label']+"_"+score
            results[uris[t_i]]=[terms_info[t_i][1],terms_info[t_i][2], terms_info[t_i][4], terms_info[t_i][0], documents[t_i], sentiment]
        num_results=len(indices)
        first_topic=topics[indices[0]]
        fig1=topic_model.visualize_barchart([first_topic], n_words=10)
        bar_plot = fig1.to_json()
        return render_template('topic_modelling.html', topic_name=topic_name, results=results, bar_plot=bar_plot, num_results=num_results) 
            
    return render_template('topic_modelling.html')

@app.route("/topic_summarization", methods=["GET"])
def topic_summarization():
    return render_template('summary.html')
        
@app.route("/evolution_of_terms", methods=["GET"])
def evolution_of_terms():
    return render_template('evolution.html')

@app.route("/defoe_queries", methods=["GET"])
def defoe_queries():
    return render_template('defoe.html')
