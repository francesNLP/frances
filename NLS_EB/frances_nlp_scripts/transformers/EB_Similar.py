#!/usr/bin/env python
# coding: utf-8

from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np

with open('terms_definitions_final.txt', 'rb') as fp:
    sentences = pickle.load(fp)

#Compute embeddings
model = SentenceTransformer('all-mpnet-base-v2')
print("Phase1")

paraphrases = util.paraphrase_mining(model, sentences, corpus_chunk_size=len(sentences), top_k=20)
print("Phase2")
with open('paraphrases_mpnet.txt', 'wb') as fp4:
    pickle.dump(paraphrases, fp4)

paraphrases_index_first=[x[1] if len(x) == 3 else None for x in paraphrases]
with open('paraphrases_index_first.txt', 'wb') as fp4:
    pickle.dump(paraphrases_index_first, fp4)

paraphrases_index_second=[x[2] if len(x) == 3 else None for x in paraphrases]
with open('paraphrases_index_second.txt', 'wb') as fp4:
    pickle.dump(paraphrases_index_second, fp4)

