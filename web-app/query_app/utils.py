from .doc2vec_prep_sparql import stem_text, clean_text
from gensim.models.doc2vec import Doc2Vec
 
def most_similar(model, text, clean_func=clean_text, topn=None):
    vector = model.infer_vector(clean_func(text), epochs=100, alpha=model.alpha, min_alpha=model.min_alpha)
    simdocs = model.docvecs.most_similar(positive=[vector], topn=topn)
    return simdocs

def load_model(filename):
    return Doc2Vec.load(filename, mmap='r')


