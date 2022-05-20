#!/usr/bin/env python
# coding: utf-8

# # Metadata-  NLS -  Encyclopaedia Britannica
# 

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


# In[3]:


import chart_studio.plotly as py
import plotly.figure_factory as ff
import plotly.express as px


# In[4]:


import networkx as nx
import matplotlib.pyplot as plt


# In[5]:


#!python -m spacy download en_core_web_sm


# In[6]:


import spacy


# In[7]:


nlp = spacy.load("en_core_web_sm")


# ### Functions

# In[8]:


def create_graph_df(df, num=None):
    if num:
        graph_df = nx.from_pandas_edgelist(df.head(n=num), source='permanentURL', target='supplementsTo', edge_attr=True, create_using=nx.MultiDiGraph())
    
    else: 
        graph_df = nx.from_pandas_edgelist(df, source='permanentURL', target='supplementsTo', edge_attr=True, create_using=nx.MultiDiGraph())

    return graph_df


# In[9]:


def explore_a_edition(df, URL):
    #term_df= df[df['term'].str.contains(term)]
    ed_df = df[df["permanentURL"]==URL]
    G = create_graph_df(ed_df)
    plt.figure(figsize=(5,5))
    pos = nx.spring_layout(G, k = 0.5) # k regulates the distance between nodes
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)
    plt.show()


# In[10]:


def read_query_results(filename):
    with open('../../results_NLS/'+filename, 'r') as f:
        query_results = safe_load(f)
    return query_results


# In[11]:


def write_query_results(filename, results):
    with open('../../results_NLS/'+filename, 'w') as f:
        documents = yaml.dump(results, f)


# In[12]:


def find_persons(text):
    doc2 = nlp(text)
    
    # Identify the persons
    persons = [ent.text for ent in doc2.ents if ent.label_ == 'PERSON']
    
    # Return persons
    return persons


# In[13]:


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


# In[26]:


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
    print(numberOfVolumes)
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

# In[15]:


query_results=read_query_results('eb_metadata_details.txt')


# In[27]:


metadata_results = copy.deepcopy(query_results)


# In[28]:


adding_metadata(metadata_results)


# In[29]:


df= create_dataframe(metadata_results)


# In[19]:


df. columns


# - MMSID: Metadata Management System ID
# - editionTitle:        Title of the edition
# - editionSubTilte:     Subtitle of the edition
# - editor:              Editor (person) of an edition or a supplement
# - termsOfAddress:      Terms of Address of the editor (e.g. Sir)
# - editor_date: Year of Birth - Year of Death
# - genre:        genre of the editions
# - language:     language used to write the volumes
# - numberOfPages: number of pages of a volume
# - physicalDescription: physical description of a edition
# - place: place printed of a edition or a supplement
# - publisher: publisher (organization or person) of an edition
# - referencedBy: books which reference an edition
# - shelfLocator: shelf locator of an edition
# - subTitle: subtitle of an edition
# - volumeTitle: title of a volume
# - year: year of print
# - volumeId: volume identifier
# - metsXML: XML mets file
# - permanentURL: URL of a volume
# - publisherPersons: list of publishers which are persons
# - volumeNum: Number of a volume
# - letters: Letters of a volume
# - part: Part of a volume
# - editionNum: Number of an editior
# - supplementTitle: Supplement subTitle
# - supplementsTo: List of editions which a supplement supplements to
# - numberOfVolumes: Number of volumes per edition or supplement

# In[20]:


df.loc[0]


# In[31]:


df.groupby(df["year"])["MMSID"].count()


# In[21]:


df.loc[0]["publisherPersons"]


# In[22]:


df[(df["editionNum"]==3)]["editionSubTitle"]


# In[23]:


df.to_json(r'../../results_NLS/metadata_eb_dataframe', orient="index") 


# In[24]:


df[["publisher", "publisherPersons"]]


# In[25]:


df[(df["volumeTitle"].str.contains("Supplement"))]


# In[26]:


df[(df["editionNum"]==3)]


# In[27]:


df[(df["supplementTitle"]!="")]["MMSID"]


# In[28]:


df["editor"]


# In[29]:


df.groupby(df["editor"]).count()


# In[30]:


df.groupby(df["publisher"]).count()


# In[31]:


df.groupby(df["editionNum"]).count()


# In[32]:


df.loc[31]


# In[33]:


df.loc[104]


# In[34]:


df_editions=df[df["editionNum"]!=0]
fig = px.line(df_editions, x="editionTitle", y="numberOfPages", title='Number of pages per edition and volume')
fig.show()


# In[35]:


fig = px.bar(df_editions, x="editionNum", y="numberOfPages", title='Number of pages per eddition and per volume / aggreagated per eddition', color="editionNum", barmode="group")
fig.show()


# In[36]:


df_by_ed=df_editions.groupby(["editionNum"])
a=df_by_ed['volumeNum'].count().reset_index()


# In[37]:


a


# In[38]:


fig = px.pie(a, values='volumeNum', names='editionNum', title='Volumes per edition', color='editionNum')
fig.show()


# In[39]:


df_supplements=df[df["editionNum"]==0]
fig = px.line(df_supplements, x="volumeTitle", y="numberOfPages", title='Number of pages per supplement')
fig.show()


# In[40]:


df[df["supplementTitle"]!=""]


# In[41]:


df=df[df["supplementTitle"]!=""]
df=df.explode('supplementsTo')


# In[42]:


graph_df = create_graph_df(df)


# In[43]:


plt.figure(figsize=(10,10))

pos = nx.spring_layout(graph_df)
nx.draw(graph_df, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)
plt.show()


# In[44]:


explore_a_edition(df, "https://digital.nls.uk/191253807")


# In[45]:


explore_a_edition(df,"https://digital.nls.uk/192693395")


# In[ ]:





# In[ ]:




