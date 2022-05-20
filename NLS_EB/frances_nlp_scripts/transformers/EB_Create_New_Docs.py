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


with open('topics_uris.txt', 'rb') as fp:
    topics_uris = pickle.load(fp)
with open ('terms_definitions.txt', 'rb') as fp2:
    documents = pickle.load(fp2)
with open('terms_uris.txt', 'rb') as fp3:
    uris = pickle.load(fp3)

indices_ed=["1_1771","1_1773","2","3", "3_supplement", "4",\
             "5","6","7", "8"]

print("Phase 2")
for ed in indices_ed:
    print("EDITION %s" %ed)
    cont=0
    filename_i='indices_%s.txt'%(ed)
    with open(filename_i, 'rb') as fp4:
        indices= pickle.load(fp4)
    filename_t='topics_summary_%s.txt'%(ed)
    with open(filename_t, 'rb') as fp5:
        topics_summary= pickle.load(fp5)
    for i in indices:
        uri=topics_uris[i]
        index_i=uris.index(uri)
        documents[index_i]=topics_summary[cont]
        cont=cont+1
    
print("FINISH")
with open('topics_summaries_total.txt', 'wb') as fp:
    pickle.dump(documents, fp)

print("SAVED")
