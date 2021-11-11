from flask import Flask, render_template, request, jsonify, session
from .flask_app import app
import requests
import traceback
from .forms import SPARQLform
from .sparql_queries import *
from flask_paginate import Pagination, get_page_parameter
import itertools
from itertools import islice

@app.route("/", methods=["GET"])
def home_page():
    return render_template('home.html')

@app.route("/term_search",  methods=['GET', 'POST'])
def term_search():
    
    headers=["Year", "Edition", "Volume", "Definition", "Related Terms"]
    
    if request.method == "POST":
        term = request.form["search"]
        if not term:
            term = "ABACISCUS"
        term=term.upper()
        session['term'] = term
    
    term=session.get('term')
    results=get_definition(term)
    page = int(request.args.get("page", 1))
    page_size=2
    per_page = 2
    offset = (page-1) * per_page
    limit = offset+per_page
    results_for_render=dict(islice(results.items(),offset, limit))
    pagination = Pagination(page=page, total=len(results), per_page=page_size, search=False)
    print("next %s, prev %s " %(pagination.has_next, pagination.has_prev))
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
            return render_template('eb_details.html', edList=edList,  ed_r=ed_r, ed_v=ed_v, ed_st=ed_st)
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
def visualization_resources():
    if 'resource_uri' in request.form:
        uri_raw=request.form.get('resource_uri').strip().replace("<","").replace(">","")
        if uri_raw == "":
            uri="<https://w3id.org/eb/i/Article/992277653804341_144133901_ABACISCUS_0>"
        else:
            uri="<"+uri_raw+">"
        g_results=describe_resource(uri)
        return render_template('visualization_resources.html', g_results=g_results)
    return render_template('visualization_resources.html')
