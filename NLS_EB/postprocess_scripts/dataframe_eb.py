#!/usr/bin/env python
# coding: utf-8

# # Merging EB terms-  NLS -  Encyclopaedia Britannica
# 

# ### Loading the necessary libraries



import yaml
import numpy as np
import collections
import string
import copy
import sys

import pandas as pd
from yaml import safe_load
from pandas.io.json import json_normalize
from difflib import SequenceMatcher


# ### Functions


def create_dataframe(query_results):
  
    
    for edition in query_results:
        for page in query_results[edition]:
            #print(page[1].keys())
            column_list=list(page[1].keys())
            break
        break
        
    data=[]
    for edition in query_results:
        for page in query_results[edition]:
            try:
                data.append(page[1])
               
            except:
                pass

    df = pd.DataFrame(data, columns = column_list)
    #removing the columns that I dont need 
    df= df.drop(['last_term_in_page', 'model', 'num_articles', 'num_page_words', 'num_text_unit' , 'text_unit', 'type_archive'], axis=1)
    #renaming the page num
    df= df.rename(columns={"text_unit_id": "start_page", "type_page": "type_article"})
    #removing 'Page' from the string
    df["start_page"] = df["start_page"].str.replace("Page", "")
    df["start_page"] = df["start_page"].astype(int)
    df["end_page"] = df["end_page"].astype(int)
    df["volume"] = 0
    df["letters"] = ""
    df["part"] = 1

    mask = df["edition"].str.contains('Volume')
    for i in range(0, len (mask)):
        if mask[i]:
            tmp=df.loc[i,'edition'].split("Volume")[1].split(",")
            if len(tmp)>1:
                volume= tmp[0]
                letters = tmp[-1]
                part_tmp = volume.split("Part")
                if len(part_tmp)>1:
                    try:
                        part = int(par_tmp[1].replace("Part ", ""))
                    except:
                        print("ERROR - PART %s, part_tmp[1]")
                        part = par_tmp[1].replace("Part ", "")
                else:
                    part=0
                volume = int(volume.replace(" ", ""))
            df.loc[i,letters] = letters
            df.loc[i,part] = part
            df.loc[i,volume] = volume
            
    df['term'] = df["term"].str.replace("_def", "")
    df['term']= df["term"].str.replace('[^a-zA-Z0-9]', '')
    mask=df["term"].str.isalpha()
    df=df.loc[mask] 
    df['term'] = df['term'].str.upper()
    df["edition_num"] = "0" 

    list_editions={"1":["first", "First"], "2":["second", "Second"],"3":["third", "Third"],               "4":["fourth", "Fourth"],                "5":["fifth","Fifth"], "6":["sixth","Sixth"],               "7":["seventh", "Seventh"], "8":["eighth", "Eighth"]} 
    
    for ed in list_editions:
        for ed_versions in list_editions[ed]:
            mask = df["edition"].str.contains(ed_versions)
            df.loc[mask, 'edition_num'] = ed
            print(ed_versions)

    df['edition_num']=df["edition_num"].astype(int)
    a=df["archive_filename"].str.split("/").str[-1]
    df['source_text_file']= a+ "/" + df["source_text_file"]   
    df= df.drop(['edition', 'archive_filename'], axis=1)
    
    
    df = df[["term", "definition", "related_terms", "num_article_words", "header", "start_page", "end_page",  "term_id_in_page", "type_article", "edition_num", "volume", "letters", "year", "title",  "place", "source_text_file"  ]]
    
    df = df[df['term'] != '']
    
    return df


def create_dataframe_from_file(filename):
    with open('../results_NLS/'+filename, 'r') as f:
        query_results = safe_load(f)
    
    df = create_dataframe(query_results)
    return df



def main():
    print(sys.argv, len(sys.argv))
    filename=sys.argv[1]
    df=create_dataframe_from_file(filename)
    includeKeywords=["Article", "Topic", "Mix"]
    df=df[df["type_article"].str.contains('|'.join(includeKeywords))]
    df.to_json(r'../results_NLS/'+filename+'_postprocess_dataframe', orient="index")

if __name__ == "__main__":
    main()
