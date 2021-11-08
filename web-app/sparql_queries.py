
def get_editor():
    sparql = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
    sparql.setQuery("""
        PREFIX eb: <https://w3id.org/eb#>
        SELECT DISTINCT ?name
        WHERE {
        ?instance eb:editor ?Editor.
        ?Editor eb:name ?name .
       }

    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"][0]["name"]["value"]


def get_year():
    sparql = SPARQLWrapper("http://localhost:3030/edition1st/sparql")
    sparql.setQuery("""
        PREFIX eb: <https://w3id.org/eb#>
        SELECT ?year WHERE {
        ?edition a eb:Edition .
        ?edition eb:publicationYear ?year 
        }

    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"][0]["year"]["value"]

