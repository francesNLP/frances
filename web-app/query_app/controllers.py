from flask import Flask, render_template, request
from .flask_app import app
from SPARQLWrapper import SPARQLWrapper, RDF, JSON
import requests
import traceback
from .forms import SPARQLform

sparqlW = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
def get_editor():
    sparqlW.setQuery("""
        PREFIX eb: <https://w3id.org/eb#>
        SELECT DISTINCT ?name
        WHERE {
        ?instance eb:editor ?Editor.
        ?Editor eb:name ?name .
       }

    """)
    sparqlW.setReturnFormat(JSON)
    results = sparqlW.query().convert()
    return results["results"]["bindings"][0]["name"]["value"]

def get_editions():
    sparql = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
    query1="""
    PREFIX eb: <https://w3id.org/eb#>
    SELECT ?enum ?e ?y WHERE {
           ?e a eb:Edition ;
                eb:number ?enum ;
                eb:publicationYear ?y.
               
        }"""
    query = query1
    sparqlW.setQuery(query)
    sparqlW.setReturnFormat(JSON)
    results = sparqlW.query().convert()
    clean_r={}
    for r in results["results"]["bindings"]:
        clean_r[r["e"]["value"]]="Edition " + r["enum"]["value"]+ " Year "+r["y"]["value"]
    return clean_r


def get_numberOfVolumes(uri):
    sparql = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
    query="""
    PREFIX eb: <https://w3id.org/eb#>
    SELECT (COUNT (DISTINCT ?v) as ?count)
        WHERE {
            %s eb:hasPart ?v.
    	    ?v ?b ?c
    }
    """ % (uri)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"][0]["count"]["value"]


def get_editions_details(uri=None):
    sparql = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
    if not uri:
       uri="<https://w3id.org/eb/i/Edition/992277653804341>"
    query="""
    PREFIX eb: <https://w3id.org/eb#>
    SELECT ?genre ?publicationYear ?num ?title ?subtitle ?printedAt ?physicalDescription ?mmsid ?shelfLocator ?numberOfVolumes  WHERE {
           %s eb:publicationYear ?publicationYear ;
              eb:number ?num;
              eb:title ?title;
              eb:subtitle ?subtitle ;
              eb:printedAt ?printedAt;
              eb:physicalDescription ?physicalDescription;
              eb:mmsid ?mmsid;
              eb:shelfLocator ?shelfLocator;
              eb:genre ?genre. 
    }
    """ % (uri)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    clean_r={}
    for r in results["results"]["bindings"]:
        clean_r["publicationYear"]=r["publicationYear"]["value"]
        clean_r["num"]=r["num"]["value"]
        clean_r["uri"]=uri
        clean_r["title"]=r["title"]["value"]
        if "subtitle" in r:
            clean_r["subtitle"]=r["subtitle"]["value"]
        else:
            clean_r["subtitle"]="No value"
        clean_r["printedAt"]=r["printedAt"]["value"]
        clean_r["physicalDescription"]=r["physicalDescription"]["value"]
        clean_r["mmsid"]=r["mmsid"]["value"]
        clean_r["shelfLocator"]=r["shelfLocator"]["value"]
        clean_r["genre"]=r["genre"]["value"]
        clean_r["language"]="English"
        clean_r["numberOfVolumes"]=get_numberOfVolumes(uri)

    return clean_r


def get_definition(term=None):
    term=term.upper()
    query1="""
    PREFIX eb: <https://w3id.org/eb#>
    SELECT ?definition ?article  ?year ?vnum ?enum ?rn WHERE {
       ?article a eb:Article ;
                eb:name "%s" ;
                eb:definition ?definition ;
                OPTIONAL {?article eb:relatedTerms ?rt.
                          ?rt eb:name ?rn.}

       ?e eb:hasPart ?v.
       ?v eb:number ?vnum.
       ?v eb:hasPart ?article.
       ?e eb:publicationYear ?year.
       ?e eb:number ?enum.
       }
    """ % (term)
    query = query1
    sparqlW.setQuery(query)
    sparqlW.setReturnFormat(JSON)
    results = sparqlW.query().convert()
    clean_r={}
    for r in results["results"]["bindings"]:
        if "rn" in r:
            clean_r[r["article"]["value"]]=[r["year"]["value"], r["enum"]["value"], r["vnum"]["value"],  r["definition"]["value"], r["rn"]["value"]]
        else:
            clean_r[r["article"]["value"]]=[r["year"]["value"], r["enum"]["value"], r["vnum"]["value"],  r["definition"]["value"]]

    return clean_r

@app.route("/", methods=["GET"])
def home_page():
    return render_template('home.html')

@app.route("/", methods=["POST"])
def rs():
        results={}
        headers=["Year", "Edition", "Volume", "Definition", "Related Terms"]
        term = request.form["search"]
        if not term:
           term = "ABACISCUS"
        term=term.upper()
        results=get_definition(term)
        return render_template("results.html",
                                                        form=SPARQLform(),
                                                        results=results,
                                                        headers=headers,
                                                        term=term
                                                        )

@app.route("/eb_details", methods=['GET', 'POST'])
def eb_details():
    edList=get_editions()
    if 'edition_selection' in request.form:
        uri_raw=request.form.get('edition_selection')
        uri="<"+uri_raw+">"
        print("Uri is %s" %uri)
        ed_r=get_editions_details(uri)
        return render_template('eb_details.html', edList=edList, ed_r=ed_r)
    return render_template('eb_details.html', edList=edList)

@app.route("/evolution_terms", methods=["GET"])
def evolution_terms():
    return render_template('evolution_terms.html')
