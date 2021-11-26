from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

def load_data(input_path_embed, file_name):
    with open (os.path.join(input_path_embed, file_name), 'rb') as fp:
        data = pickle.load(fp)
    return data

def get_topic_name(index_uri, topics, topic_model):
    topic_num=topics[index_uri]
    topic_info=topic_model.get_topic(topic_num)
    topic_name="" 
    #lets get the first 4 elements
    cont = 0
    for i in topic_info:
        topic_name=topic_name+"_"+i[0]
        cont=cont+1
        if cont == 4:
           break
    topic_name=str(topic_num)+topic_name
    return topic_name

def calculating_similarity_text(definition, text_embeddings, model, terms_info, documents, uris, topics_names, topics, sentiment_terms):
    definition_embedding= model.encode(definition, batch_size = 8, show_progress_bar = True)
    similarities=cosine_similarity( [definition_embedding], text_embeddings)
    similarities_sorted = similarities.argsort()
    results={}
    topics_vis=[]
    for i in range(-1, -12, -1):
        similar_index=similarities_sorted[0][i]
        rank=similarities[0][similar_index]
        score='%.2f'%sentiment_terms[similar_index][0]['score']
        sentiment = sentiment_terms[similar_index][0]['label']+"_"+score
        topic_name = topics_names[similar_index]
        if topics[similar_index] not in topics_vis:
            topics_vis.append(topics[similar_index])
        results[uris[similar_index]]=[terms_info[similar_index][1],terms_info[similar_index][2], terms_info[similar_index][4], terms_info[similar_index][0], documents[similar_index], topic_name, rank, sentiment]
    return results, topics_vis

