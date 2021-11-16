from doc2vec_prep_sparql import stem_text, clean_text
from sparql_queries  import get_document
import gensim
from gensim.models.doc2vec import Doc2Vec
 
def most_similar(model, text, clean_func=clean_text, topn=None):
    vector = model.infer_vector(clean_func(text), epochs=100, alpha=model.alpha, min_alpha=model.min_alpha)
    simdocs = model.docvecs.most_similar(positive=[vector], topn=topn)
    return simdocs

def load_model(filename):
    return Doc2Vec.load(filename, mmap='r')


model=load_model('../../NLS_EB/results_NLS/doc2vec_sparql_ed1.model')

definition="is also the name of an ancient instrument for facilitating operations in arithmetic. It is vadoully contrived. That chiefly used in Europe is made by drawing any number of parallel lines at the di(lance of two diameters of one of the counters used in the calculation. A counter placed on.the lowed line, signifies r; on the sd, 10; on the 3d, 100; on the 4th, 1000, &c. In the intermediate spaces, the same counters are eflimated at one Jialf of the value of the line immediately superior, viz. between the id and 2d, 5; between the 2d and 3d, 50, &c. See plate I. fig. 2. A B, where the same number, 1768 for example, is represented under both by different dispositions of the counters."

term="ABACUS"
text=term+definition
simdocs=most_similar(model, text, topn=10)

for uri, rank in simdocs:
         term, definition = get_document(uri)
         print("Document_id: %s - Rank %s - Details: Term %s, Definition: %s" %(uri, rank, term, definition))
         print("---")


