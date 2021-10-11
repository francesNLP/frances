# frances

## 1. Extracting Encyclopaedia Britannica Articles using DEFOE

- Defoe is able to extract articles from the EB volumes.
- We have stored these data stored in [NLS_EB/results_NLS/](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)results_eb_[1|2|3|4 ...]_edition.
- We have 8 editions 

## 2. PostProcessing Articles using Notebooks 

- The data extracted from defoe needs further postprocess. We do that using [Merging_EB_Terms.ipynb](https://github.com/francesNLP/frances/blob/main/NLS_EB/Merging_EB_Terms.ipynb)
- [Merging_EB_Terms.ipynb](https://github.com/francesNLP/frances/blob/main/NLS_EB/Merging_EB_Terms.ipynb) cleans each of the results_NLS/results_eb_[1|2|3|4 ...]_edition files, creating a new clean version of them: [NLS_EB/results_NLS/](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)results_eb_[1|2|3|4 ...]_edition**_updated**.

- Furthermore, this notebook re-arrange these data to create dataframe, with the following columms:

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

This dataframe is also stored in [NLS_EB/results_NLS/](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)results_eb_[1|2|3|4 ...]_edition_postprocess_dataframe. 

## 3. Questions

Here a list of questions that we want to ask to these data



## 4. Architecture


<img width="1194" alt="FrancesArchitecture" src="https://user-images.githubusercontent.com/6940078/134651770-deafc0a8-0dab-4144-a933-151db978e0ad.png">


## 5. ElasticSearch

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
