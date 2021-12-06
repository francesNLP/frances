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

with open('documents_summaries_1ed.txt', 'rb') as fp:
    documents = pickle.load(fp)
with open('terms_info_1ed.txt', 'rb') as fp2:
    terms_info = pickle.load(fp2)
with open('uris_1ed.txt', 'rb') as fp3:
    uris = pickle.load(fp3)

model = SentenceTransformer('all-mpnet-base-v2')
text_embeddings_new = model.encode(documents, batch_size = 8, show_progress_bar = True)
all_embeddings_1ed = np.array(text_embeddings_new)
np.save('embeddings_summaries_1ed_mpnet.npy', all_embeddings_1ed)
#text_embeddings_new = np.load('embeddings_summaries_1ed_new.npy')

similarities = cosine_similarity(text_embeddings_new)
similarities_sorted = similarities.argsort()
with open ('similarities_summaries_1ed_mpnet.txt', 'wb') as fp3:
     pickle.dump(similarities, fp3)
with open('similarities__summaries_sorted_1ed_mpnet.txt', 'wb') as fp4:
    pickle.dump(similarities_sorted, fp4)




