from flask import Flask, render_template, request, jsonify, session
from .flask_app import app
import requests
import traceback
from .sparql_queries import *
from flask_paginate import Pagination, get_page_parameter
import itertools
from itertools import islice
from .utils import load_model, most_similar

model=load_model('/Users/rosafilgueira/HW-Work/NLS-Fellowship/work/frances/web-app/models/doc2vec_sparql_ed1.model')

@app.route("/", methods=["GET"])
def home_page():
    return render_template('home.html')

@app.route("/term_search/<string:termlink>",  methods=['GET', 'POST'])
@app.route("/term_search",  methods=['GET', 'POST'])
def term_search(termlink=None):
    
    headers=["Year", "Edition", "Volume", "Start Page", "End Page", "Term Type", "Definition", "Related Terms"]
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
                                           term=term)
       

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
                text=data_similar
                uri_raw=""                
            if uri_raw!="":
                uri="<"+uri_raw+">"
                term, definition, enum, year, vnum  =get_document(uri)
                text=term+definition
            simdocs=most_similar(model, text, topn=11)
            results={}
            cont = 0
            for r_uri_raw, rank in simdocs:
                if r_uri_raw!=uri_raw :
                    r_uri="<"+r_uri_raw+">"
                    r_term, r_definition,r_enum, r_year, r_vnum = get_document(r_uri)
                    results[r_uri_raw]=[r_enum, r_year, r_vnum, r_term, r_definition, rank]
                    cont+=1
                if cont == 10:
                    break 
            if uri_raw == "":
                return render_template('similar.html', results=results)
            else:
                return render_template('similar.html', results=results, term=term, definition=definition, uri=uri_raw, enum=enum, year=year, vnum=vnum)
    
    termlink  = request.args.get('termlink', None)
    termtype  = request.args.get('termtype', None)
    if termlink!=None:
        if ">" in termlink:
            termlink=termlink.split(">")[0]
        uri="<https://w3id.org/eb/i/"+termtype+"/"+termlink+">"
        term, definition, enum, year, vnum  =get_document(uri)
        text=term+definition
        simdocs=most_similar(model, text, topn=11)
        results={}
        cont = 0
        for r_uri_raw, rank in simdocs:
             if r_uri_raw!=termlink:
                 r_uri="<"+r_uri_raw+">"
                 r_term, r_definition,r_enum, r_year, r_vnum = get_document(r_uri)
                 results[r_uri_raw]=[r_enum, r_year, r_vnum, r_term, r_definition, rank]
                 cont+=1
             if cont == 10:
                 break 
        return render_template('similar.html', results=results, term=term, definition=definition, uri=uri, enum=enum, year=year, vnum=vnum)
    return render_template('similar.html')

@app.route("/topic_summarization", methods=["GET"])
def topic_summarization():
    return render_template('summary.html')
        
@app.route("/evolution_of_terms", methods=["GET"])
def evolution_of_terms():
    return render_template('evolution.html')

@app.route("/defoe_queries", methods=["GET"])
def defoe_queries():
    return render_template('defoe.html')
