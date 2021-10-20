#!/usr/bin/env python
# coding: utf-8

# # Metadata-  NLS -  Encyclopaedia Britannica
# 

# ### Loading the necessary libraries

# In[2]:


import yaml
import numpy as np
import collections
import string
import copy

import pandas as pd
from yaml import safe_load
from pandas.io.json import json_normalize
from difflib import SequenceMatcher
import spacy
nlp = spacy.load("en_core_web_sm")

# ### Functions

def read_query_results(filename):
    with open('../results_NLS/'+filename, 'r') as f:
        query_results = safe_load(f)
    return query_results


def write_query_results(filename, results):
    with open('../results_NLS/'+filename, 'w') as f:
        documents = yaml.dump(results, f)


def find_persons(text):
    doc2 = nlp(text)
    
    # Identify the persons
    persons = [ent.text for ent in doc2.ents if ent.label_ == 'PERSON']
    
    # Return persons
    return persons


def adding_metadata(query_results):
     for i in query_results:
        volume_id=i.split("/")[-1]
        mets_xml = volume_id+ "-mets.xml"
        query_results[i]["volumeId"] = volume_id
        query_results[i]["metsXML"] = mets_xml
        query_results[i]["permanentURL"] = "https://digital.nls.uk/"+volume_id
        if query_results[i]["referenced_by"]:
            query_results[i]["referenced_by"]=query_results[i]["referenced_by"].split("----")
        if query_results[i]["publisher"]:
            persons=find_persons(query_results[i]["publisher"])
            query_results[i]["publisherPersons"]=persons
        else:
            query_results[i]["publisherPersons"]=None

def create_dataframe(metadata_results):
  
    for i in metadata_results:
        column_list=list(metadata_results[i].keys())
        break
        
    data=[]
    for i in metadata_results:
        data.append(metadata_results[i])
    df = pd.DataFrame(data, columns = column_list)
    
    df= df.rename(columns={"edition":"editionTitle", "subtitle":"editionSubTitle",
                           "title":"volumeTitle", "referenced_by":"referencedBy",\
                           "num_pages":"numberOfPages", "name_termsOfAddress":"termsOfAddress", 
                           "physical_description": "physicalDescription"})
    
   
    df= df.drop(['geographic', 'country', 'topic', 'city', 'temporal', 'dateIssued'], axis=1)
    df["genre"] = "encyclopedia"
    df["volumeNum"] = 0
    df["letters"] = ""
    df["part"] = 0
    
    
    mask = df["editionTitle"].str.contains('Volume')
    for i in range(0, len (mask)):
     
        if mask[i]:
            tmp=df.loc[i,'editionTitle'].split("Volume ")[1].split(",")
            if len(tmp)>=1:
                volume= tmp[0]
                letters = tmp[-1].replace(" ","")
                part_tmp = volume.split("Part ")
                if len(part_tmp)>1:
                    volume=part_tmp[0]
                    part = part_tmp[1]
    
                    try:
                        part = int(part)
                    except:
                        if "I" in part:
                            part = 1
                else:
                    part=0

                volume = int(volume)
                df.loc[i, "letters"] = letters
                df.loc[i,"part"] = part
                df.loc[i ,"volumeNum"] = volume
      
            
    df["editionNum"] = "0"
    list_editions={"1":["first", "First"], "2":["second", "Second"],"3":["third", "Third"],
                   "4":["fourth", "Fourth"], "5":["fifth","Fifth"], "6":["sixth","Sixth"], 
                   "7":["seventh", "Seventh"], "8":["eighth", "Eighth"]}
    
    for ed in list_editions:
        for ed_versions in list_editions[ed]:
            mask = df["editionTitle"].str.contains(ed_versions)
            df.loc[mask, 'editionNum'] = ed
            
            
    df['editionNum']=df["editionNum"].astype(int)    
    df["supplementTitle"]=""
    df["supplementSubTitle"]=""
    df["supplementsTo"]=""
    
    mask= df["volumeTitle"].str.contains("Supplement")
    for i in range(0, len (mask)):
        if mask[i]:
            df.loc[i, 'supplementTitle'] = df.loc[i, 'volumeTitle']
            df.loc[i, 'supplementSubTitle'] = df.loc[i, 'editionSubTitle']
            df.loc[i, 'editionSubTitle'] = ""
            df.loc[i, 'volumeTitle'] = df.loc[i, 'volumeTitle'] + ","+df.loc[i, 'editionTitle']
            title= df.loc[i, 'supplementTitle']
            related_editions=[]
            for ed in list_editions:
                for ed_versions in list_editions[ed]:
                    if ed_versions in title:
                        related_editions.append(ed)
                        
            df.loc[i, "supplementsTo"]=','.join(related_editions)
    
    df["supplementsTo"] = df.supplementsTo.str.split(",").tolist()
    df["numberOfVolumes"]=0
    
    numberOfVolumes=df.groupby(df["editionNum"])["MMSID"].count().to_dict()
    for i in range(1, len(numberOfVolumes)):
        
        df.loc[(df['editionNum']==i),"numberOfVolumes"]=numberOfVolumes[i]
            
    df_sup=df[df["supplementTitle"]!=""]
    numberOfVolumesSup=df_sup.groupby(df_sup["supplementTitle"]).count()["MMSID"].to_dict()
    
    for i in numberOfVolumesSup:
        df.loc[(df['supplementTitle']==i),"numberOfVolumes"]=numberOfVolumesSup[i]
        

    return df

# ### 1. Reading data

# Here we are going to take the output of the defoe files, and we are going to merge the terms that splitted across pages. 
# 
# The next line takes time!

query_results=read_query_results('../results_NLS/eb_metadata_details.txt')

## adding some metadata
adding_metadata(query_results)

## create a dataframe
df= create_dataframe(query_results)

## saving it to a file
df.to_json(r'../results_NLS/metadata_eb_dataframe', orient="index") 

