from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity

def calculating_similarity_text(definition, text_embeddings, model, terms_info, documents, uris):
    definition_embedding= model.encode(definition, batch_size = 8, show_progress_bar = True)
    similarities=cosine_similarity( [definition_embedding], text_embeddings)
    similarities_sorted = similarities.argsort()
    results={}
    for i in range(-1, -12, -1):
        similar_index=similarities_sorted[0][i]
        rank=similarities[0][similar_index]
        results[uris[similar_index]]=[terms_info[similar_index][1],terms_info[similar_index][2], terms_info[similar_index][4], terms_info[similar_index][0], documents[similar_index], rank]
    return results

