# frances

## 1. Extracting automatically articles from the Encyclopaedia Britannica (EB)

Finally, we have created a [new defoe query for extracting automatically articles](https://github.com/francesNLP/defoe/blob/master/defoe/nlsArticles/queries/write_articles_pages_df_yaml.py) from the EB. The articles are stored per edition in YAML files.  

Here we have the command for running this query for extracting the articles of the first, assuming that we are located in the [defoe](https://github.com/francesNLP/defoe) directory. 

```
spark-submit --py-files defoe.zip defoe/run_query.py nls_first_edition.txt nlsArticles defoe.nlsArticles.queries.write_articles_pages_df_yaml queries/writehdfs.yml -r frances/ results_NLS/results_eb_1_edition] -n 34 
```

**Important**: For doing this work, instead of adding this query under the defoe NLS model, we have created a new one, called **nlsArticles** [model]((https://github.com/francesNLP/defoe/blob/master/defoe/nlsArticles). This is because, for extracting automatically the articles from the pages, it required to introduce specific modifications at the page and archive level - for capturing headers and text columns. Therefore, this query under **nlsArticles and not under nls**.  

Note that for running this query you need configuration file for specifying the operating system and the defoe path for the *long_s fix*:
- [configuration_file](https://github.com/francesNLP/defoe/blob/master/queries/write_to_yml.yml)


We have stored these data stored in [NLS_EB/results_NLS/](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)results_eb_[1|2|3|4 ...]_edition.

And We have **8 editions**. So, we have 8 extracted EB_Articles YAML files in total!! 

## 2. Extracted EB_Articles metadata 

Each YAML file has a row per article found within a page, with the following columns (being the most important **term** and **definition**):
 
 - title: title of the book (e.g. Encyclopaedia Britannica)
 - edition: edition of the book (e.g Eighth edition, Volume 2, A-Anatomy)
 - year: year of publication/edition (e.g. 1853)
 - place: place (e.g. Edinburgh)      
 - archive_filename: directory path of the book (e.g. /home/rosa_filgueira_vicente/datasets/single_EB/193322698/)     
 - source_text_filename: directory Path of the page (e.g. alto/193403113.34.xml)
 - text_unit: unit that represent each ALTO XML. These could be Page or Issue. 
 - text_unit_id: id of the page (e.g. Page704)
 - num_text_unit: number of pages (e.g. 904)
 - type_archive: type of archive. Thse could be book or newspapers. 
 - model: defoe model used for ingesting this dataset (nlsArticles)
 - type_page: the page classification that has been done by defoe. These could be Topic, Articles, Mix or Full Page. 
 - header: the header of the page (e.g. AMERICA)
 - **term**: term that is going to be described (e.g. AMERICA)
 - **definition**: words describing an article / topic/ full page: ( e.g. “AMERICA. being inhabited. The Aleutian ….”)
 - num_articles: number of articles per page. In case a page has been classified as Topic or FullPage, the number of articles is 1.
 - num_page_words: number of words per page (e.g. 1373)
 - num_article_words: number of words of an article (e.g. 1362)
 
We have detected two types of articles with two different patterns at “page” level:
  - *Short articles* (named as **articles**): Usually presented by a TERM in the main text in uppercase,  followed by a “,”  (e.g. ALARM, ) and then a DESCRIPTION of the TERM (similar to an entry in a dictionary). This description normally is one or two paragraphs, but of course there are exceptions.  	
	- Term: ALARM
	- Definition: in the Military Art, denotes either the apprehension of being suddenly attacked, or the notice thereof signified by firing a cannon, firelock, or the like. False alarms are frequently made use of to harass the enemy, by keeping them constantly under arms. , ….
 
- *Long articles* (named as **topics**): In this is the case, the Encyclopaedia introduces a TERM in the header of a page (which is not the case for the short articles), and then it normally uses several pages to describe that topic (and very often it uses a combination of text, pictures, tables, etc.). For example, the “topic” AMERICA goes from page 677 to 724 (47 pages!)
 
Important: **Topic** is just the way we named the *long articles* that expands more than a page. It does not refer to “NLP topic”.


## 3. PostProcessing EB_Articles 

We have realised that those articles need further postprocess, in order to merge articles and topics across pages, and doing futher cleaning. 
Therefore, we have created [Merging_EB_Terms.ipynb](https://github.com/francesNLP/frances/blob/main/NLS_EB/Merging_EB_Terms.ipynb), a notebook that cleans each of the results_NLS/results_eb_[1|2|3|4 ...]_edition files, and creates a new  version of them: [NLS_EB/results_NLS/](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)results_eb_[1|2|3|4 ...]_edition**_updated**.

Furthermore, this notebook re-arrange the information in EB_Articles to create a dataframe per file, with **NEW COLUMNS**:

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
	- type_article:        Type of Page [Full Page| Topic| Mix | Articles]                                       
	- year:                Year of the Volume
	- volume:              Volume (e.g. 1)
	- letters:             Leters of the volume (A-B)
	
** THESE ARE THE PROPERTIES THAT WE ARE GOING TO WORK WITH FROM NOW ON**

This dataframe is also stored in [NLS_EB/results_NLS/](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)results_eb_[1|2|3|4 ...]_edition_postprocess_dataframe. 

## 4. Questions

Here a list of questions that we want to ask to these data:

- Search by term
- Number of terms per edition
- Compare terms across edition
- Obtain a graph with the related terms per term
- Obtain similar terms



## 5. Architecture


<img width="1194" alt="FrancesArchitecture" src="https://user-images.githubusercontent.com/6940078/134651770-deafc0a8-0dab-4144-a933-151db978e0ad.png">


## 6. ElasticSearch

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
