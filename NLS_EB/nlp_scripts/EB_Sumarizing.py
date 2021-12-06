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


with open ('topics_documents_1ed.txt', 'rb') as fp:
    topics_documents = pickle.load(fp)
with open('topics_info_1ed.txt', 'rb') as fp2:
    topics_info = pickle.load(fp2)
with open('topics_uris_1ed.txt', 'rb') as fp3:
    topics_uris = pickle.load(fp3)
with open('indices_1771.txt', 'rb') as fp4:
    indices_1771 = pickle.load(fp4)
with open('indices_1773.txt', 'rb') as fp5:
    indices_1773 = pickle.load(fp5)


model = TransformerSummarizer(transformer_type="XLNet",transformer_model_key="xlnet-base-cased")

topics_summary_1771=[]
cont=0
for i in indices_1771:
    print("Summary-1771 %s" %cont)
    text=topics_documents[i]
    try:
        full = ''.join(model(text, min_length=60))
        topics_summary_1771.append(full)
    except:
        print("Error in %s" %cont)
        topics_summary_1771.append(["Not avaiable"])
    cont=cont+1
    
print("FINISH TOPICS 1771")
with open('topics_summary_1771.txt', 'wb') as fp:
    pickle.dump(topics_summary_1771, fp)


topics_summary_1773=[]
cont=0
for i in indices_1773:
    print("Summary-1773 %s" %cont)
    text=topics_documents[i]
    try:
        full = ''.join(model(text, min_length=60))
        topics_summary_1773.append(full)
    except:
        print("Error in %s" %cont)
        topics_summary_1773.append(["Not avaiable"])
    cont=cont+1

print("FINISH TOPICS 1773")
with open('topics_summary_1773.txt', 'wb') as fp:
    pickle.dump(topics_summary_1773, fp)

