#!/usr/bin/env python
# coding: utf-8

# # Exploring Terms in the Encyclopaedia Britannica
# 
# ## Similar terms within an edition - all-mpnet-base-v2 - Transformers
# 
# 
# https://theaidigest.in/how-to-do-semantic-document-similarity-using-bert/

# ### Loading the necessary libraries

# In[1]:


from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np

with open('terms_definitions_final.txt', 'rb') as fp:
    documents = pickle.load(fp)

model = SentenceTransformer('all-mpnet-base-v2')
model._first_module().max_seq_length = 509
text_embeddings_new = model.encode(documents, show_progress_bar = True)
all_embeddings_total_ed = np.array(text_embeddings_new)
np.save('embeddings_mpnet.npy', all_embeddings_total_ed)
print("embeddings finished and saved")

print("finished")




