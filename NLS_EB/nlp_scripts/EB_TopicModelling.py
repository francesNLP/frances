#!/usr/bin/env python
# coding: utf-8

# # Exploring Terms in the Encyclopaedia Britannica
# 
# ## Similar terms within an edition - BERT - Transformers
# 
# 
# https://theaidigest.in/how-to-do-semantic-document-similarity-using-bert/

# ### Loading the necessary libraries

# In[80]:


import os
from bertopic import BERTopic
import pandas as pd
import pickle
import numpy as np

def get_topic_name(index_uri, topics, topic_model):
    topic_num=topics[index_uri]
    topic_info=topic_model.get_topic(topic_num)
    topic_name=""
    #lets get the first 4 elements
    cont = 0
    for i in topic_info:
        topic_name=topic_name+"_"+i[0]
        cont=cont+1
        if cont == 4:
            break
    topic_name=str(topic_num)+topic_name
    return topic_name


with open('documents_summaries_1ed.txt', 'rb') as fp:
    documents = pickle.load(fp)
with open('terms_info_1ed.txt', 'rb') as fp2:
    terms_info = pickle.load(fp2)
with open('uris_1ed.txt', 'rb') as fp3:
    uris = pickle.load(fp3)

embeddings = np.load('embeddings_summaries_1ed_mpnet.npy')

topic_model = BERTopic(min_topic_size=20).fit(documents, embeddings)
topics, probs = topic_model.transform(documents, embeddings)


t_names=[]
topics_names=[]
for i in range(0, len(topics)):
    topic_name=get_topic_name(i, topics, topic_model)
    if topic_name not in t_names:
        t_names.append(topic_name)
    topics_names.append(topic_name)

topic_model.save("BerTopic_Model_mpnet_summaries")
with open('topics_1_ed_mpnet_summaries.txt', 'wb') as fp:
    pickle.dump(topics, fp)

with open('t_names_1_ed_mpnet_summaries.txt', 'wb') as fp:
    pickle.dump(t_names, fp)

with open('topics_names_1_ed_mpnet_summaries.txt', 'wb') as fp:
    pickle.dump(topics_names, fp)




