#!/usr/bin/env python
# coding: utf-8

# ## OCR - Detecting errors - Cleaning with ELMO
# 
# 
# https://github.com/neuspell

# ### Loading the necessary libraries

# In[1]:


import numpy as np
import collections
import os
from neuspell import ElmosclstmChecker
import pickle

with open('documents_summaries_1ed.txt', 'rb') as fp:
    documents = pickle.load(fp)

checker= ElmosclstmChecker()
checker.from_pretrained()
clean_documents_elmo=[]

cont=0
for raw1 in documents:
    try:
        clean_documents_elmo.append(checker.correct(raw1))
    except:
        clean_documents_elmo.append(raw1)
    cont=cont+1

print("FINISH CLEANING")
with open('clean_documents_ElmosclstmChecker_summaries_1ed.txt', 'wb') as fp:
    pickle.dump(clean_documents_elmo, fp)

