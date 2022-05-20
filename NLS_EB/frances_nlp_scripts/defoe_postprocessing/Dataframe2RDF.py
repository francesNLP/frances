#!/usr/bin/env python
# coding: utf-8

# # RDF-   NLS -  Encyclopaedia Britannica
# 
# 
# For each postprocess edition dataframe that we got from **Merging_EB_Terms.ipynb** (e.g. results_eb_1_edition_dataframe, results_eb_2_edition_dataframe, etc) we are going to add the information from the dataframe that we got from **Metadata_EB.ipynb** (metadata_eb_dataframe). 
# 
# The idea is to have per edition dataframe (and also supplement dataframe), all the information (which currently is splitted across several dataframes) in one. 
# 
# 
# This notebook will store the final dataframes in results_NLS directory, and their name schema will be **final_eb_< NUM_EDITION >_dataframe**.
# 
# Per entry in these new dataframes we will have the following columns (see an example of one entry of the first edition):
# 
# - MMSID:                                              
# - editionTitle:                          First edition, 1771, Volume 1, A-B
# - editor:                                                  Smellie, William
# - editor_date:                                                   1740-1795
# - genre:                                                       encyclopedia
# - language:                                                             eng
# - termsOfAddress:                                                       NaN
# - numberOfPages:                                                        832
# - physicalDescription:               3 v., 160 plates : ill. ; 26 cm. (4to)
# - place:                                                         Edinburgh
# - publisher:              Printed for A. Bell and C. Macfarquhar; and so...
# - referencedBy:           [Alston, R.C.  Engl. language III, 560, ESTC T...
# - shelfLocator:                                                        EB.1
# - editionSubTitle:        Illustrated with one hundred and sixty copperp...
# - volumeTitle:            Encyclopaedia Britannica; or, A dictionary of ...
# - year:                                                                1771
# - volumeId:                                                       144133901
# - metsXML:                                               144133901-mets.xml
# - permanentURL:                            https://digital.nls.uk/144133901
# - publisherPersons:                     [C. Macfarquhar, Colin Macfarquhar]
# - volumeNum:                                                              1
# - letters:                                                              A-B
# - part:                                                                   0
# - editionNum:                                                             1
# - supplementTitle:                                                         
# - supplementSubTitle:                                                      
# - supplementsTo:                                                         []
# - numberOfVolumes:                                                        6
# - term:                                                                  OR
# - definition:             A NEW A D I C T I A A, the name of several riv...
# - relatedTerms:                                                          []
# - header:                                           EncyclopaediaBritannica
# - startsAt:                                                              15
# - endsAt:                                                                15
# - numberOfTerms:                                                         22
# - numberOfWords:                                                         54
# - positionPage:                                                           0
# - typeTerm:                                                         Article
# - altoXML:                                  144133901/alto/188082904.34.xml

# ### Loading the necessary libraries


import yaml
import numpy as np
import collections
import string
import copy
from datetime import datetime


import pandas as pd
from yaml import safe_load
from pandas.io.json import json_normalize
from difflib import SequenceMatcher



def edition2rdf(data, g, eb):

    edition = URIRef("https://w3id.org/eb/i/Edition/"+str(data["MMSID"]))
    edition_title= "Edition "+ str(data["editionNum"])+"," +str(data["year"])
    g.add((edition, RDF.type, eb.Edition))
    g.add((edition, eb.number, Literal(data["editionNum"], datatype=XSD.integer)))
    g.add((edition, eb.title, Literal(edition_title, datatype=XSD.string)))
    g.add((edition, eb.subtitle, Literal(data["editionSubTitle"], datatype=XSD.string)))
    g.add((edition, eb.publicationYear, Literal(data["year"], datatype=XSD.integer)))
    g.add((edition, eb.printedAt, Literal(data["place"], datatype=XSD.string)))
    g.add((edition, eb.mmsid, Literal(str(data["MMSID"]), datatype=XSD.string)))
    g.add((edition, eb.physicalDescription, Literal(data["physicalDescription"], datatype=XSD.string)))
    g.add((edition, eb.genre, Literal(data["genre"], datatype=XSD.string)))
    g.add((edition, eb.language, Literal(data["language"], datatype=XSD.string)))
    g.add((edition, eb.shelfLocator, Literal(data["shelfLocator"], datatype=XSD.string)))
    g.add((edition, eb.numberOfVolumes, Literal(data["numberOfVolumes"], datatype=XSD.integer)))

    #### Editor 

    if data["editor"]!=0.0:
        name=data["editor"].replace(" ", "")
        
        editor = URIRef("https://w3id.org/eb/i/Person/"+str(name))
        g.add((editor, RDF.type, eb.Person))
        g.add((editor, eb.name, Literal(data["editor"], datatype=XSD.string)))

        if data["editor_date"]!=0:
            tmpDate=data["editor_date"].split("-")
            birthDate=datetime.strptime(tmpDate[0], '%Y')
            deathDate=datetime.strptime(tmpDate[1], '%Y')
            g.add((editor, eb.birthDate, Literal(birthDate, datatype=XSD.dateTime)))
            g.add((editor, eb.deathDate, Literal(deathDate, datatype=XSD.dateTime)))
    
        if (data["termsOfAddress"]!= 0) or (data["termsOfAddress"]!= 0.0) :
             g.add((editor, eb.termsOfAddress, Literal(data["termsOfAddress"], datatype=XSD.string)))
        g.add((edition, eb.editor, editor))

    #### Publishers Persons 

    #This was the result to pass entity recognition to publisher

    if data["publisherPersons"] != 0:
        publisherPersons=name=data["publisherPersons"]
        for p in publisherPersons: 
            name=p.replace(" ", "")
            publisher = URIRef("https://w3id.org/eb/i/Person/"+name)
            g.add((publisher, RDF.type, eb.Person))
            g.add((publisher, eb.name, Literal(p, datatype=XSD.string)))
            g.add((edition, eb.publisher, publisher))
        
    #### Is Referenced by  

    if data["referencedBy"] != 0:
        references=data["referencedBy"]
        for r in references: 
            name=r.replace(" ", "")
            book = URIRef("https://w3id.org/eb/i/Book/"+name)
            g.add((book, RDF.type, eb.Book))
            g.add((book, eb.title, Literal(r, datatype=XSD.string)))
            g.add((edition, eb.referencedBy, book))
            
    return g, edition
        


# ### 1. Loading the final dataframe


dfs = [] # an empty list to store the data frames
file_list=['../../results_NLS/final_eb_1_dataframe', '../../results_NLS/final_eb_2_dataframe', '../../results_NLS/final_eb_3_dataframe',          '../../results_NLS/final_eb_4_dataframe', '../../results_NLS/final_eb_5_dataframe', '../../results_NLS/final_eb_6_dataframe',          '../../results_NLS/final_eb_7_dataframe', '../../results_NLS/final_eb_8_dataframe']
for file in file_list:
    print("file %s" % file)
    data = pd.read_json(file, orient="index")  # read data frame from json file
    dfs.append(data) # append the data frame to the list

df = pd.concat(dfs, ignore_index=True) # concatenate all the data frames in the list.


tt= pd.read_json('../../results_NLS/final_eb_2_dataframe', orient="index") 
tt=tt.fillna(0)
tt_year=tt.reset_index(drop=True)
df=df.fillna(0)
df_year=df.reset_index(drop=True)
related_df_entries=df_year[df_year["term"] == "DRAWING"].reset_index(drop=True)
related_df_entries["relatedTerms"]
vl=related_df_entries["volumeNum"].unique()
# Lets get the first element of the "final_eb_1_dataframe" dataframe and extract the information of the 1st Edition class.
# ### 2. Create a Graph and import the information of  all Editions  to it.  


from rdflib import Graph, URIRef, Literal, Namespace, XSD
from rdflib.namespace import RDF, RDFS


# Create a Graph
g = Graph()

g.namespace_manager.bind('eb', Namespace("https://w3id.org/eb#"), override="False")
eb = Namespace("https://w3id.org/eb#")

#### 

list_years=df["year"].unique()
ed_revisions=[]
print("list_years %s" %list_years)

for y in range(0, len(list_years)):
    
    ### EDITION
    print("YEAR %s" %list_years[y])
    
    df_year=df[df['year'] == list_years[y]].reset_index(drop=True)
    edition_data = df_year.loc[0]
    g, edition = edition2rdf(edition_data,g, eb)
    ed_revisions.append(edition)
    
    ### VOLUMES 
    list_vols = df_year["volumeNum"].unique()
    for v in range(0,len(list_vols)):
        print("Vol %s" % list_vols[v])
        df_year_vl=df_year[df_year["volumeNum"] == list_vols[v]].reset_index(drop=True)
        volume_data=df_year_vl.loc[0]
        volume_id=volume_data["volumeId"]
        volume = URIRef("https://w3id.org/eb/i/Volume/"+str(volume_data["MMSID"])+"_"+str(volume_data["volumeId"]))
        g.add((volume, RDF.type, eb.Volume))
        g.add((volume, eb.number, Literal(volume_data["volumeNum"], datatype=XSD.integer)))
        g.add((volume, eb.letters, Literal(volume_data["letters"], datatype=XSD.string)))
        g.add((volume, eb.volumeId, Literal(volume_data["volumeId"], datatype=XSD.int)))
        g.add((volume, eb.title, Literal(volume_data["volumeTitle"], datatype=XSD.string)))
        
        if volume_data["part"]!=0:
            g.add((volume, eb.part, Literal(volume_data["part"], datatype=XSD.string)))
    
        g.add((volume, eb.metsXML, Literal(volume_data["metsXML"], datatype=XSD.string)))
        g.add((volume, eb.permanentURL, Literal(volume_data["permanentURL"], datatype=XSD.string)))
        g.add((volume, eb.numberOfPages, Literal(volume_data["numberOfPages"], datatype=XSD.string)))
    
        g.add((edition, eb.hasPart, volume))
    
        df_by_term=df_year_vl.groupby(['term'],)["term"].count().reset_index(name='counts')
                        
        #### TERMS
        for t_index in range(0, len(df_by_term)):
            t=df_by_term.loc[t_index]["term"]
            c=df_by_term.loc[t_index]["counts"]
            df_entries= df_year_vl[df_year_vl["term"] == t].reset_index(drop=True)
            for t_count in range(0, c):
                df_entry= df_entries.loc[t_count]
                if df_entry["typeTerm"] == "Article" :
                    term= URIRef("https://w3id.org/eb/i/Article/"+str(df_entry["MMSID"])+"_"+str(df_entry["volumeId"])+"_"+t+"_"+str(t_count))
                    g.add((term, RDF.type, eb.Article))
                elif df_entry["typeTerm"] == "Topic" :
                    term= URIRef("https://w3id.org/eb/i/Topic/"+str(df_entry["MMSID"])+"_"+str(df_entry["volumeId"])+"_"+t+"_"+str(t_count))
                    g.add((term, RDF.type, eb.Topic))
                else:
                    pass
                g.add((term, eb.name, Literal(t, datatype=XSD.string)))
                g.add((term, eb.definition, Literal(df_entry["definition"], datatype=XSD.string)))
                g.add((term, eb.position, Literal(df_entry["positionPage"], datatype=XSD.int)))
                g.add((term, eb.numberOfWords, Literal(df_entry["numberOfWords"], datatype=XSD.int)))
                g.add((volume, eb.hasPart, term))
            
                ## startsAt
                page_startsAt= URIRef("https://w3id.org/eb/i/Page/"+ str(df_entry["MMSID"])+"_"+str(df_entry["volumeId"])+"_"+str(df_entry["startsAt"]))
                g.add((page_startsAt, RDF.type, eb.Page))
                g.add((page_startsAt, eb.number, Literal(df_entry["startsAt"], datatype=XSD.int)))
                g.add((page_startsAt, eb.header, Literal(df_entry["header"], datatype=XSD.string)))
                g.add((page_startsAt, eb.numberOfTerms, Literal(df_entry["numberOfTerms"], datatype=XSD.int)))
                g.add((volume, eb.hasPart, page_startsAt))
                g.add((term, eb.startsAtPage, page_startsAt))
                g.add((page_startsAt, eb.hasPart, term))
            
                ## endsAt
                page_endsAt= URIRef("https://w3id.org/eb/i/Page/"+ str(df_entry["MMSID"])+"_"+str(df_entry["volumeId"])+"_"+str(df_entry["endsAt"]))
                g.add((page_endsAt, RDF.type, eb.Page))
                g.add((page_endsAt, eb.number, Literal(df_entry["endsAt"], datatype=XSD.int)))
                g.add((volume, eb.hasPart, page_endsAt))
                g.add((term, eb.endsAtPage, page_endsAt))
                g.add((page_endsAt, eb.hasPart, term))
                
                ## related terms
                
                if df_entry["relatedTerms"]:
                    for rt in df_entry["relatedTerms"]:
                        if rt!= t:
                            related_df_entries= df_year[df_year["term"] == rt].reset_index(drop=True)
                            list_r_vl=related_df_entries["volumeNum"].unique()
                            for r_vl in list_r_vl:
                                df_r_vl=related_df_entries[related_df_entries["volumeNum"] == r_vl].reset_index(drop=True)
                                for r_c in range (0, len(df_r_vl)):
                                    r_entry= df_r_vl.loc[r_c]
                                    if r_entry["typeTerm"] == "Article" :
                                        r_term= URIRef("https://w3id.org/eb/i/Article/"+str(r_entry["MMSID"])+"_"+str(r_entry["volumeId"])+"_"+rt+"_"+str(r_c))
                                    elif r_entry["typeTerm"] == "Topic" :
                                        r_term= URIRef("https://w3id.org/eb/i/Topic/"+str(r_entry["MMSID"])+"_"+str(r_entry["volumeId"])+"_"+rt+"_"+str(r_c))
                                        
                                    g.add((term, eb.relatedTerms, r_term))
                        



g.add((ed_revisions[1], eb.revisionOf, ed_revisions[0]))


# Save the Graph in the RDF Turtle format
g.serialize(format="turtle", destination="../../results_NLS/total_eb.ttl")


