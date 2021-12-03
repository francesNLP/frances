from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os, yaml
from query_app.defoe_query_utils import preprocess_word, parse_preprocess_word_type

#### Matplotlib plots
import matplotlib.pyplot as plt
from io import BytesIO
import base64

### Plotly plots
import chart_studio.plotly as py
import plotly.figure_factory as ff
import pandas as pd
import plotly.express as px

###
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
    for i in range(-1, -21, -1):
        similar_index=similarities_sorted[0][i]
        rank=similarities[0][similar_index]
        score='%.2f'%sentiment_terms[similar_index][0]['score']
        sentiment = sentiment_terms[similar_index][0]['label']+"_"+score
        topic_name = topics_names[similar_index]
        if topics[similar_index] not in topics_vis:
            topics_vis.append(topics[similar_index])
        results[uris[similar_index]]=[terms_info[similar_index][1],terms_info[similar_index][2], terms_info[similar_index][4], terms_info[similar_index][0], documents[similar_index], topic_name, rank, sentiment]
    return results, topics_vis


def preprocess_lexicon(data_file, preprocess="normalize"):
    keysentences=[]
    preprocess_type=parse_preprocess_word_type(preprocess)
    print("---the preprocess type is %s" %preprocess_type)
    with open(data_file, 'r') as f:
        for keysentence in list(f):
            k_split = keysentence.split()
            sentence_word = [preprocess_word(word,preprocess_type) for word in k_split]
            sentence_norm = ''
            for word in sentence_word:
                if sentence_norm == '':
                    sentence_norm = word
                else:
                    sentence_norm += " " + word
            keysentences.append(sentence_norm)
    return keysentences

def dict_defoe_queries():
    defoe_q={}
    defoe_q["target_keysearch_by_year_filter_date"]="target_keysearch_by_year_filter_date"
    defoe_q["target_keysearch_by_year"]="target_keysearch_by_year"
    defoe_q["keysearch_by_year"]="keysearch_by_year"
    defoe_q["keysearch_by_year_details"]="keysearch_by_year_details.py"
    return defoe_q


def read_results(results_file):
    with open(results_file, "r") as stream:
            results=yaml.safe_load(stream)
    return results



def freq_count(results):
    freq_count={}
    for year in results:
        for i in results[year]:
            if i[0] not in freq_count:
                freq_count[i[0]]={}
                freq_count[i[0]][year]=i[1]
                
            else:
                if year not in freq_count[i[0]]:
                    freq_count[i[0]][year]=i[1]
                else:    
                    freq_count[i[0]][year]+=i[1]
    return freq_count

def normalize_freq(publication, freq_results, view_terms):
    fig=plt.figure(figsize=(20,8))
    years=set()
    for term in view_terms:
        if term in freq_results:
            normed_results = {}
            for year in freq_results[term]:
                if year>0:
                    normed_results[year] = (freq_results[term][year]* len(term.split()))/float(publication[year][2])
                    years.add(year)
            plt.plot(*zip(*sorted(normed_results.items())), label=term, lw = 2, alpha = 1, marker="X")
    x_years=sorted(list(years))
    plt.xticks(np.arange(min(x_years), max(x_years)+1, 2.0), rotation=45) 
    plt.ticklabel_format(style = 'plain')
    plt.tick_params(axis='both', which='major', labelsize=10)
    plt.legend(loc='upper left')
    plt.xlabel("Years")
    plt.ylabel("Normalized Frequency")
    return fig




def plot_freq_count(freq_results, view_terms):
    img = BytesIO()
    years=set()
    for term in view_terms:
        if term in freq_results:
            plt.plot(*zip(*sorted(freq_results[term].items())), label=term, lw = 2, alpha = 1, marker="X")
            for y in freq_results[term].keys(): 
                years.add(y)     
    plt.xticks(sorted(list(years)), rotation=50)
    #plt.ticklabel_format(axis="y"style = 'plain')
    plt.legend(loc='upper right')
    plt.ylabel('Frequency')
    plt.xlabel("Years")
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url

def plotly_freq_count(f_count):
    df=pd.DataFrame.from_dict(f_count)
    fig = px.line(df, labels={
                     "index": "Year",
                     "value": "Frequency",
                     "variable": "Lexicon"
                 }, title="Frequency of Lexicon Terms per Years")
    return fig

def plot_taxonomy_freq(taxonomy, results):

    f_count=freq_count(results)
    plot_url=plotly_freq_count(f_count)
    return plot_url


