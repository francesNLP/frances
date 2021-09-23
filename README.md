# frances

## ElasticSearch

Terminal 1:

1. Download elasticsearch-7.11.2.
2. Decompress the elastic search-7.11.2 folder
3. cd elasticsearch-7.11.2/
4. ./bin/elasticsearch 
           (Let it running - do not close this terminal)

Terminal  2) 
1. python create_load_indexes.py   —> It creates an ES index (nlsArticles) and loads the json files into Elastic Search. 
2. curl 'localhost:9200/_cat/indices?v’  —> It checks that the index and data have been created correctly in Elastic Search
3. python train_model_es.py.  —> Train a doc2vec model using the data previously loaded to Elastic Search 
4. python test_load_search_model_es.py. —> Test the doc2vec model and retrieve the most similar documents (of a given text) from Elastic Search.  
