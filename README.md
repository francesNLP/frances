# frances

## DATA FROM DEFOE

- Defoe is able to extract articles from the EB volumes.
- We have stored these data stored in NLS_EB/results_NLS/results_eb_[1|2|3|4 ...]_edition.
- We have 8 editions 

## PostProcess Encyclpedia

- The data extracted from defoe needs further postprocess. We do that using Merging_EB_Terms.ipynb
- Merging_EB_Terms clean each of the results_NLS/results_eb_[1|2|3|4 ...]_edition files, created a clean version of them, and storing them in results_NLS/results_eb_[1|2|3|4 ...]_edition_updated.

- Furthermore, that notebook create a dataframe, with the following columms:

	- definition:           Definition of the article
	- edition_num:          1,2,3,4,5,6,7,8
	- header:               Header of the page's article                                  
	- num_article_words:    Number of words per article
	- place:                Place where the volume was edited (e.g. Edinburgh)                                    
	- related_terms:        Related articles (see X article)  
	- source_text_file:     File Path of the XML file from which the article belongs       
	- term:                 Article name                            
	- term_id_in_page:      Number of article in the page     
	- start_page:           Number page in which the article starts 
	- end_page:             Number page in which the article ends 
	- title:               Title of the Volume
	- type_article:            Type of Page [Full Page| Topic| Mix | Articles]                                       
	- year:                 Year of the Volume
	- volume:               volume (e.g. 1)
	- letters:              leters of the volume (A-B)
	
** THESE ARE THE COLUMNS/PROPERTIES THAT WE ARE GOING TO USE **

## QUESTIONS

Here a list of questions that we want to ask to these data



## Architecture


<img width="1194" alt="FrancesArchitecture" src="https://user-images.githubusercontent.com/6940078/134651770-deafc0a8-0dab-4144-a933-151db978e0ad.png">


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
