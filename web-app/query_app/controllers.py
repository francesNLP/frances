from flask import Flask, render_template, request, jsonify
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


def describe_resource(uri=None):
   sparql = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
   query="""
   PREFIX eb: <https://w3id.org/eb#>
   DESCRIBE %s 
   """ % (uri)
   sparql.setQuery(query)
   results = sparql.query().convert()
   clear_r=[]
   for s,p,o in results.triples((None, None, None)):
       data={}
       sub=str(s)
       if "#" in sub:
           sub=sub.split("#")[1]
           sub="eb:"+sub
       data["subject"]=sub
       pred=str(p)
       if "#" in pred:
           pred=pred.split("#")[1]
           pred="eb:"+pred
       data["predicate"]=pred
       obj=str(o)
       if "#" in obj:
           obj=obj.split("#")[1]
           obj="eb:"+obj
       
       if len(obj)>80:
          obj=obj[0:80]
          obj=obj+"... CONTINUE"

       data["object"]=obj
       clear_r.append(data)

   startsAtPage="-1"
   endsAtPage="-2"

   for i in range(0, len(clear_r)):
       if "startsAtPage" in clear_r[i]["predicate"]:
           startsAtPage= clear_r[i]["object"]
       if "endsAtPage" in clear_r[i]["predicate"]:
           endsAtPage= clear_r[i]["object"]
           endsAtPageIndex =i

 
   if startsAtPage == endsAtPage:
       clear_r.pop(endsAtPageIndex)
   return clear_r

def get_volumes(uri):
    sparql = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
    query="""
    PREFIX eb: <https://w3id.org/eb#>
    SELECT ?v ?vnum ?part ?letters WHERE {
       %s eb:hasPart ?v .
       ?v eb:number ?vnum ; 
          eb:letters ?letters .
          OPTIONAL {?v eb:part ?part; }
    } 
    """ % (uri)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    r=results["results"]["bindings"]
    clean_r={}
    for i in r:
       if "part" in i:
           clean_r[i["v"]["value"]]= i["vnum"]["value"]+ " "+ i["letters"]["value"]+ "Part "+ i["part"]["value"]
       else:
           clean_r[i["v"]["value"]]= i["vnum"]["value"]+ " "+ i["letters"]["value"]
   
    return clean_r



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
        clean_r["Year"]=r["publicationYear"]["value"]
        clean_r["Edition Number"]=r["num"]["value"]
        clean_r["Edition URI"]=uri
        clean_r["Edition Title"]=r["title"]["value"]
        if "subtitle" in r:
            clean_r["Edition Subtitle"]=r["subtitle"]["value"]
        clean_r["Printed at"]=r["printedAt"]["value"]
        clean_r["Physical Description"]=r["physicalDescription"]["value"]
        clean_r["MMSID"]=r["mmsid"]["value"]
        clean_r["Shelf Locator"]=r["shelfLocator"]["value"]
        clean_r["Genre"]=r["genre"]["value"]
        clean_r["Language"]="English"
        clean_r["Number of Volumes"]=get_numberOfVolumes(uri)

    return clean_r

def get_volume_details(uri=None):
    sparql = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
    query="""
    PREFIX eb: <https://w3id.org/eb#>
    SELECT ?num ?title ?part ?metsXML ?volumeId ?permanentURL ?numberOfPages ?letters WHERE {
       %s eb:number ?num ;
          eb:title ?title;
          eb:metsXML ?metsXML;
          eb:volumeId ?volumeId;
          eb:permanentURL ?permanentURL;
          eb:numberOfPages ?numberOfPages;
          eb:letters ?letters.
       OPTIONAL {%s eb:part ?part. }
      
               
    }
    """ % (uri, uri)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    clean_r={}
    for r in results["results"]["bindings"]:
        clean_r["Volume Number"]=r["num"]["value"]
        clean_r["Volume URI"]=uri
        clean_r["Volume Title"]=r["title"]["value"]
        clean_r["Volume Letters"]=r["letters"]["value"]
        if "part" in r:
            clean_r["Volume Part"]=r["part"]["value"]
        clean_r["Volume Permanent URL"]=r["permanentURL"]["value"]
        clean_r["Volume Number of Pages"]=r["numberOfPages"]["value"]
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

def get_vol_statistics(uri):
    data={}
    ###### NUM ARTICLES
    query="""
          PREFIX eb: <https://w3id.org/eb#>
          SELECT (COUNT (DISTINCT ?t) as ?count)
          WHERE {
          %s eb:hasPart ?t .
          ?t a eb:Article
         } 
         """ % (uri)
    sparqlW.setQuery(query)
    sparqlW.setReturnFormat(JSON)
    results = sparqlW.query().convert()
    num_articles=results["results"]["bindings"][0]["count"]["value"]
    data["Number of Articles"]=num_articles

    ###### NUM TOPICS
    query1="""
          PREFIX eb: <https://w3id.org/eb#>
          SELECT (COUNT (DISTINCT ?t) as ?count)
          WHERE {
          %s eb:hasPart ?t .
          ?t a eb:Topic 
         } 
         """ % (uri)
    sparqlW.setQuery(query1)
    sparqlW.setReturnFormat(JSON)
    results1 = sparqlW.query().convert()
    num_topics=results1["results"]["bindings"][0]["count"]["value"]
    data["Number of Topics"] = num_topics

    ###### NUM DIST ARTICLES
    query2="""
         PREFIX eb: <https://w3id.org/eb#>
         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
         SELECT (count (DISTINCT ?a) as ?count)
         WHERE {
            %s eb:hasPart ?b .
    	    ?b a eb:Article .
    	    ?b eb:name ?a.
        }
        """ % (uri)
    sparqlW.setQuery(query2)
    sparqlW.setReturnFormat(JSON)
    results2 = sparqlW.query().convert()
    num_dist_articles= results2["results"]["bindings"][0]["count"]["value"]
    data["Number of Distinct Articles"] = num_dist_articles


    ###### NUM DIST TOPICS
    query3="""
       PREFIX eb: <https://w3id.org/eb#>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       SELECT (count (DISTINCT ?a) as ?count)
       WHERE {
            %s eb:hasPart ?b .
    	    ?b a eb:Topic .
    	    ?b eb:name ?a.
      }
      """ % (uri)
    sparqlW.setQuery(query3)
    sparqlW.setReturnFormat(JSON)
    results3 = sparqlW.query().convert()
    num_dist_topics= results3["results"]["bindings"][0]["count"]["value"]
    data["Number of Distinct Topics"] = num_dist_topics
    return data
            

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
