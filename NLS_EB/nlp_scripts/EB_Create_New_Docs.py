#!/usr/bin/env python
import numpy as np
import collections
import pandas as pd
from summarizer import Summarizer, TransformerSummarizer
import pickle
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from collections import Counter
from heapq import nlargest


with open('topics_info_1ed.txt', 'rb') as fp2:
    topics_info = pickle.load(fp2)
with open('topics_uris_1ed.txt', 'rb') as fp3:
    topics_uris = pickle.load(fp3)
with open('indices_1771.txt', 'rb') as fp4:
    indices_1771 = pickle.load(fp4)
with open('indices_1773.txt', 'rb') as fp5:
    indices_1773 = pickle.load(fp5)

with open('topics_summary_1771.txt', 'rb') as fp:
    topics_summary_1771=pickle.load(fp)
with open('topics_summary_1773.txt', 'rb') as fp:
    topics_summary_1773=pickle.load(fp)

with open ('documents_1ed.txt', 'rb') as fp:
    documents = pickle.load(fp)
with open('terms_info_1ed.txt', 'rb') as fp2:
    terms_info = pickle.load(fp2)
with open('uris_1ed.txt', 'rb') as fp3:
    uris = pickle.load(fp3)

cont=0
for i in indices_1771:
    uri=topics_uris[i]
    index_i=uris.index(uri)
    print("voy a sustituir  TERM %s, which is also %s" %(terms_info[index_i], topics_info[i]))
    documents[index_i]=topics_summary_1771[cont]
    cont=cont+1
    
cont=0
for i in indices_1773:
    uri=topics_uris[i]
    index_i=uris.index(uri)
    print("voy a sustituir  TERM %s, which is also %s" %(terms_info[index_i], topics_info[i]))
    documents[index_i]=topics_summary_1773[cont]
    cont=cont+1
    
print("FINISH")
with open('documents_summaries_1ed.txt', 'wb') as fp:
    pickle.dump(documents, fp)

print("SAVED")
