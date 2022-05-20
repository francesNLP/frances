#!/usr/bin/env python
# coding: utf-8

# # FINAL Dataframe-  NLS -  Encyclopaedia Britannica
# 
# This notebook is going to merge all the data available that we have from our postprocess dataframes.
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

# In[1]:


import yaml
import numpy as np
import collections
import string
import copy


# In[2]:


import pandas as pd
from yaml import safe_load
from pandas.io.json import json_normalize
from difflib import SequenceMatcher


# ### Functions

# In[3]:


def add_metadata(df):
    
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
    return df


# In[4]:


def create_dataframe(df_metadata, df_data, editionNum):
    
    
    appended_data = []
    df_m_ed = df_metadata[df_metadata['editionNum'] == editionNum]
    list_years=df_m_ed["year"].unique()
    
    for y in range(0, len(list_years)):
        df_d_year=df_data[df_data['year'] == list_years[y]].reset_index(drop=True)
        df_m_year = df_m_ed[df_m_ed['year'] == list_years[y]].reset_index(drop=True)
        list_vols = df_m_year["volumeNum"].unique()
        print("YEAR %s, list_vols %s" % (list_years[y], list_vols))
        for v in range(0,len(list_vols)):
            df_d_year_vl=df_d_year[df_d_year["volumeNum"] == list_vols[v]].reset_index(drop=True)
            df_m_year_vl = df_m_year[df_m_year['volumeNum']==list_vols[v]].reset_index(drop=True)
            list_parts = df_m_year_vl["part"].unique()
            print("VOL %s, list_parts are %s" % (list_vols[v], list_parts))
            for p in range(0, len(list_parts)):
                df_d_year_vl_p=df_d_year_vl[df_d_year_vl["part"] == list_parts[p]].reset_index(drop=True)
                df_m_year_vl_p=df_m_year_vl[df_m_year_vl["part"] == list_parts[p]].reset_index(drop=True)
            
                
                d_rows_year_vl_p=len(df_d_year_vl_p.index)-1
                print("number of data rows for year %s, vol %s and part %s is %s" % (list_years[y], list_vols[v], list_parts[p], d_rows_year_vl_p ))
        
                df_m_year_vl_p_f = df_m_year_vl_p.append([df_m_year_vl_p]*d_rows_year_vl_p,ignore_index=True).reset_index(drop=True)
                result = pd.concat([df_m_year_vl_p_f, df_d_year_vl_p], axis=1).reset_index(drop=True)
                print("Len of the new temporal concatenated df %s" %len(result.index))
                appended_data.append(result)
    
    if editionNum == 3:
        df_m_sup = df_m[df_m['supplementTitle'].str.contains("third")]
        list_years=df_m_sup["year"].unique()
        
        for y in range(0, len(list_years)):
            df_d_year=df_data[df_data['year'] == list_years[y]].reset_index(drop=True)
            df_m_year = df_m_sup[df_m_sup['year'] == list_years[y]].reset_index(drop=True)
            list_vols = df_m_year["volumeNum"].unique()
            print("SUP YEAR %s, list_vols %s" % (list_years[y], list_vols))
            for v in range(0,len(list_vols)):
                df_d_year_vl=df_d_year[df_d_year["volumeNum"] == list_vols[v]].reset_index(drop=True)
                df_m_year_vl = df_m_year[df_m_year['volumeNum']==list_vols[v]].reset_index(drop=True)
                list_parts = df_m_year_vl["part"].unique()
                print("SUP VOL %s, list_parts are %s" % (list_vols[v], list_parts))
                for p in range(0, len(list_parts)):
                    df_d_year_vl_p=df_d_year_vl[df_d_year_vl["part"] == list_parts[p]].reset_index(drop=True)
                    df_m_year_vl_p=df_m_year_vl[df_m_year_vl["part"] == list_parts[p]].reset_index(drop=True)
            
                
                    d_rows_year_vl_p=len(df_d_year_vl_p.index)-1
                    print("SUP number of data rows for year %s, vol %s and part %s is %s" % (list_years[y], list_vols[v], list_parts[p], d_rows_year_vl_p ))
        
                    df_m_year_vl_p_f = df_m_year_vl_p.append([df_m_year_vl_p]*d_rows_year_vl_p,ignore_index=True).reset_index(drop=True)
                    result = pd.concat([df_m_year_vl_p_f, df_d_year_vl_p], axis=1).reset_index(drop=True)
                    print("SUP Len of the new temporal concatenated df %s" %len(result.index))
                    appended_data.append(result)
                
                
    final_df = pd.concat(appended_data).reset_index(drop=True)
    final_df =  final_df.loc[:,~final_df.columns.duplicated()]
    return final_df


# In[5]:


def create_dataframe_sup(df_metadata, df_data):

    appended_data=[]
    df_m_sup = df_m[df_m['supplementTitle'].str.contains("fourth")]
    list_years=df_m_sup["year"].unique()
        
    for y in range(0, len(list_years)):
        df_d_year=df_data[df_data['year'] == list_years[y]].reset_index(drop=True)
        df_m_year = df_m_sup[df_m_sup['year'] == list_years[y]].reset_index(drop=True)
        list_vols = df_m_year["volumeNum"].unique()
        print("SUP YEAR %s, list_vols %s" % (list_years[y], list_vols))
        for v in range(0,len(list_vols)):
            df_d_year_vl=df_d_year[df_d_year["volumeNum"] == list_vols[v]].reset_index(drop=True)
            df_m_year_vl = df_m_year[df_m_year['volumeNum']==list_vols[v]].reset_index(drop=True)
            list_parts = df_m_year_vl["part"].unique()
            print("SUP VOL %s, list_parts are %s" % (list_vols[v], list_parts))
            for p in range(0, len(list_parts)):
                df_d_year_vl_p=df_d_year_vl[df_d_year_vl["part"] == list_parts[p]].reset_index(drop=True)
                df_m_year_vl_p=df_m_year_vl[df_m_year_vl["part"] == list_parts[p]].reset_index(drop=True)
            
                
                d_rows_year_vl_p=len(df_d_year_vl_p.index)-1
                print("SUP number of data rows for year %s, vol %s and part %s is %s" % (list_years[y], list_vols[v], list_parts[p], d_rows_year_vl_p ))
        
                df_m_year_vl_p_f = df_m_year_vl_p.append([df_m_year_vl_p]*d_rows_year_vl_p,ignore_index=True).reset_index(drop=True)
                result = pd.concat([df_m_year_vl_p_f, df_d_year_vl_p], axis=1).reset_index(drop=True)
                print("SUP Len of the new temporal concatenated df %s" %len(result.index))
                appended_data.append(result)
                
                
    final_df = pd.concat(appended_data).reset_index(drop=True)
    final_df =  final_df.loc[:,~final_df.columns.duplicated()]
    return final_df


# ### 1. Loading the metadata dataframe

# In[6]:


df_m= pd.read_json(r'../../results_NLS/metadata_eb_dataframe', orient="index")


# In[7]:


df_m[df_m["editionNum"]==3]


# ### 2. Creating the NEW final dataframes for all Editions
# 
# 
# Possible values:
# - results_eb_4_5_6_suplement_dataframe
# - results_eb_8_edition_dataframe
# - results_eb_7_edition_dataframe
# - results_eb_6_edition_dataframe
# - results_eb_5_edition_dataframe
# - results_eb_4_edition_dataframe
# - results_eb_3_edition_dataframe
# - results_eb_2_edition_dataframe
# - results_eb_1_edition_dataframe
# 

# In[8]:


df_d = pd.read_json("../../results_NLS/results_eb_1_edition_dataframe", orient="index") 
len(df_d)


# In[9]:


df_d.columns


# In[10]:


df_d.tail(3)["volumeNum"]


# Note: add_metadata function can take a while. 

# In[11]:


df_d = add_metadata(df_d)


# **IMPORTANT**
# 
# - Use create_dataframe for creating the final dataframe for all editions. This function needs to **indicate the NUMBER of the edition, in the last argument**. 
# - Use create_dataframe_sup for creating the final dataframe for the supplements. 

# In[12]:


df_final=create_dataframe(df_m, df_d, 1)
#df_final=create_dataframe_sup(df_m, df_d)


# And these are the columns of our FINAL DATAFRAME

# In[13]:


df_final.columns


# In[14]:


df_final


# ### 3. Saving new final dataframes to disk

# In[15]:


df_final.to_json(r'../../results_NLS/final_eb_1_dataframe', orient="index")


# ### 4. Loading new final dataframes to memory

# In[5]:


df = pd.read_json('../../results_NLS/final_eb_1_dataframe', orient="index") 


# In[6]:


df.head(2)


# In[7]:


df.loc[0]


# In[ ]:




